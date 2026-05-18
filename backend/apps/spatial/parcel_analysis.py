"""
Analyse automatique d'une parcelle (polygone ou zone administrative).
Combine sols terrain, indicateurs NASA et prédiction IA fertilité.
"""
from __future__ import annotations

import json
from collections import Counter
from datetime import datetime

from django.contrib.gis.geos import GEOSGeometry, Point
from django.db.models import Avg, Count, Max, Min
from django.utils import timezone

from soils.models import AdministrativeZone, SoilPoint, SoilPointNasaSnapshot

from . import services


def _geom_from_request(geometry=None, zone_code=None, zone_id=None):
    if zone_code:
        zone = AdministrativeZone.objects.filter(code=zone_code).first()
        if not zone:
            raise ValueError(f'Zone « {zone_code} » introuvable.')
        return zone.geometry, zone.name, zone.code
    if zone_id:
        zone = AdministrativeZone.objects.filter(pk=zone_id).first()
        if not zone:
            raise ValueError('Zone introuvable.')
        return zone.geometry, zone.name, zone.code
    if geometry:
        geom = GEOSGeometry(json.dumps(geometry), srid=4326)
        if geom.geom_type not in ('Polygon', 'MultiPolygon'):
            raise ValueError('Géométrie invalide : Polygon ou MultiPolygon requis.')
        return geom, 'Parcelle dessinée', None
    raise ValueError('geometry, zone_code ou zone_id requis.')


def _ndvi_status(avg_ndvi: float | None) -> str:
    if avg_ndvi is None:
        return 'donnees_manquantes'
    if avg_ndvi < 0.25:
        return 'stress_severe'
    if avg_ndvi < 0.35:
        return 'stress_modere'
    if avg_ndvi < 0.5:
        return 'vegetation_moyenne'
    return 'vegetation_vigoureuse'


def _smap_status(avg_smap: float | None) -> str:
    if avg_smap is None:
        return 'donnees_manquantes'
    if avg_smap < 0.12:
        return 'secheresse_probable'
    if avg_smap < 0.2:
        return 'humidite_faible'
    if avg_smap < 0.35:
        return 'humidite_moyenne'
    return 'humidite_bonne'


def _parcel_vulnerability(avg_slope, avg_ndvi, avg_smap) -> dict:
    score = 0
    factors = []
    slope = avg_slope or 0
    ndvi = avg_ndvi if avg_ndvi is not None else 0.45
    smap = avg_smap if avg_smap is not None else 0.25
    if slope > 5:
        score += 1
        factors.append('Pente élevée — risque d\'érosion')
    if ndvi < 0.3:
        score += 1
        factors.append('NDVI bas — stress végétatif (NASA)')
    if smap < 0.15:
        score += 1
        factors.append('Humidité sol faible (SMAP NASA)')
    if score >= 2:
        level = 'elevee'
    elif score == 1:
        level = 'moyenne'
    else:
        level = 'faible'
    return {'level': level, 'score': score, 'factors': factors}


def _dominant_soil_type(points_qs) -> str:
    types = list(points_qs.values_list('soil_type', flat=True))
    if not types:
        return 'limoneux'
    return Counter(types).most_common(1)[0][0]


def analyze_parcel(*, geometry=None, zone_code=None, zone_id=None, use_ml=True):
    geom, parcel_name, code = _geom_from_request(geometry, zone_code, zone_id)
    area = services.polygon_area(geom.geojson)

    zones_qs = services.intersection_zones(geom.geojson)
    zones_data = [
        {'code': z.code, 'name': z.name, 'zone_type': z.zone_type}
        for z in zones_qs[:20]
    ]

    points = SoilPoint.objects.filter(location__within=geom, is_validated=True)
    agg = points.aggregate(
        count=Count('id'),
        avg_ph=Avg('ph'),
        avg_humidity=Avg('humidity_pct'),
        avg_ndvi=Avg('ndvi_3m_avg'),
        avg_smap=Avg('smap_moisture_avg'),
        avg_slope=Avg('slope_pct'),
        min_ph=Min('ph'),
        max_ph=Max('ph'),
    )

    centroid = geom.centroid
    nasa_snapshots = SoilPointNasaSnapshot.objects.filter(
        soil_point__location__within=geom,
    ).values('product').annotate(avg_val=Avg('value'), n=Count('id'))

    nasa_by_product = {
        row['product']: {'avg': round(float(row['avg_val']), 4), 'samples': row['n']}
        for row in nasa_snapshots
    }

    avg_ndvi = float(agg['avg_ndvi']) if agg['avg_ndvi'] is not None else None
    avg_smap = float(agg['avg_smap']) if agg['avg_smap'] is not None else None
    avg_ph = float(agg['avg_ph']) if agg['avg_ph'] is not None else None
    avg_humidity = float(agg['avg_humidity']) if agg['avg_humidity'] is not None else None
    avg_slope = float(agg['avg_slope']) if agg['avg_slope'] is not None else None

    if avg_ndvi is None and 'MOD13Q1' in str(nasa_by_product):
        for key, val in nasa_by_product.items():
            if 'NDVI' in key.upper() or 'MOD13' in key.upper():
                avg_ndvi = val['avg']

    vulnerability = _parcel_vulnerability(avg_slope, avg_ndvi, avg_smap)

    ml_prediction = None
    recommendations = []

    if use_ml:
        from ml_predict.pipeline import predict_fertility

        soil_type = _dominant_soil_type(points) if agg['count'] else 'limoneux'
        features = {
            'ph': avg_ph or 6.0,
            'humidity_pct': avg_humidity or 35.0,
            'soil_type': soil_type,
            'slope_pct': avg_slope or 3.0,
            'ndvi_3m_avg': avg_ndvi or 0.45,
            'smap_moisture_avg': avg_smap or 0.2,
            'month': datetime.now().month,
        }
        ml_prediction = predict_fertility(features)
        if ml_prediction.get('recommendation'):
            recommendations.append(ml_prediction['recommendation'])

    if vulnerability['factors']:
        recommendations.extend(vulnerability['factors'])

    if _ndvi_status(avg_ndvi) in ('stress_severe', 'stress_modere'):
        recommendations.append(
            'Surveiller la végétation via NDVI NASA ; irrigation ou couvert végétal recommandé.',
        )
    if _smap_status(avg_smap) in ('secheresse_probable', 'humidite_faible'):
        recommendations.append(
            'Stress hydrique détecté (SMAP) : planifier irrigation ou paillage.',
        )
    if agg['count'] == 0:
        recommendations.append(
            'Aucun point de sol validé dans la parcelle — effectuer des prélèvements terrain.',
        )
    if avg_ph is not None and avg_ph < 5.5:
        recommendations.append('Sol acide : envisager un chaulage adapté au Togo.')
    elif avg_ph is not None and avg_ph > 7.5:
        recommendations.append('Sol basique : adapter les cultures (légumineuses, etc.).')

    recommendations = list(dict.fromkeys(recommendations))[:8]

    from nasa.models import NasaLayerCatalog
    active_layers = list(
        NasaLayerCatalog.objects.filter(is_active=True).values_list('product', flat=True)[:10],
    )

    return {
        'parcel_name': parcel_name,
        'zone_code': code,
        'centroid': {'lon': centroid.x, 'lat': centroid.y},
        'area': area,
        'zones_intersected': zones_data,
        'soil_points': {
            'count': agg['count'] or 0,
            'avg_ph': round(avg_ph, 2) if avg_ph is not None else None,
            'min_ph': round(float(agg['min_ph']), 2) if agg['min_ph'] is not None else None,
            'max_ph': round(float(agg['max_ph']), 2) if agg['max_ph'] is not None else None,
            'avg_humidity_pct': round(avg_humidity, 1) if avg_humidity is not None else None,
            'avg_ndvi': round(avg_ndvi, 3) if avg_ndvi is not None else None,
            'avg_smap': round(avg_smap, 3) if avg_smap is not None else None,
            'avg_slope_pct': round(avg_slope, 1) if avg_slope is not None else None,
        },
        'nasa': {
            'avg_ndvi': round(avg_ndvi, 3) if avg_ndvi is not None else None,
            'avg_smap': round(avg_smap, 3) if avg_smap is not None else None,
            'ndvi_status': _ndvi_status(avg_ndvi),
            'smap_status': _smap_status(avg_smap),
            'by_product': nasa_by_product,
            'active_catalog_layers': active_layers,
        },
        'vulnerability': vulnerability,
        'ml_prediction': ml_prediction,
        'recommendations': recommendations,
        'analyzed_at': timezone.now().isoformat(),
        'geometry_geojson': json.loads(geom.geojson),
    }
