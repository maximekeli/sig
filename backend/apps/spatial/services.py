"""PostGIS spatial analysis services — OS4."""
from django.contrib.gis.db.models.functions import Distance
from django.contrib.gis.geos import GEOSGeometry, Point
from django.contrib.gis.measure import D
from django.db.models import Avg

from soils.models import AdministrativeZone, SoilPoint


def proximity_search(lon, lat, radius_m, limit=100):
    point = Point(float(lon), float(lat), srid=4326)
    qs = (
        SoilPoint.objects.filter(location__distance_lte=(point, D(m=radius_m)))
        .annotate(distance_m=Distance('location', point))
        .order_by('distance_m')[:limit]
    )
    return [
        {
            'id': p.id,
            'ph': p.ph,
            'soil_type': p.soil_type,
            'distance_m': round(p.distance_m.m, 1),
            'lon': p.location.x,
            'lat': p.location.y,
        }
        for p in qs
    ]


def intersection_zones(geojson_geometry):
    geom = GEOSGeometry(geojson_geometry, srid=4326)
    zones = AdministrativeZone.objects.filter(geometry__intersects=geom)
    return AdministrativeZone.objects.filter(
        pk__in=zones.values_list('pk', flat=True)
    )


def buffer_geometry(geojson_geometry, distance_m):
    geom = GEOSGeometry(geojson_geometry, srid=4326)
    buffered = geom.transform(3857, clone=True)
    buffered = buffered.buffer(float(distance_m))
    buffered.transform(4326)
    return buffered.geojson


def polygon_area(geojson_geometry):
    geom = GEOSGeometry(geojson_geometry, srid=4326)
    geom_proj = geom.transform(3857, clone=True)
    area_m2 = geom_proj.area
    return {'area_m2': round(area_m2, 2), 'area_ha': round(area_m2 / 10000, 4)}


def vulnerability_zoning():
    """
    Combine slope >5%, NDVI <0.3, SMAP <15% — low/medium/high vulnerability.
    """
    results = []
    for point in SoilPoint.objects.filter(is_validated=True).iterator():
        slope = point.slope_pct or 0
        ndvi = point.ndvi_3m_avg or 0.5
        smap = point.smap_moisture_avg or 0.25
        score = 0
        if slope > 5:
            score += 1
        if ndvi < 0.3:
            score += 1
        if smap < 0.15:
            score += 1
        if score >= 2:
            level = 'elevee'
        elif score == 1:
            level = 'moyenne'
        else:
            level = 'faible'
        results.append({
            'id': point.id,
            'lon': point.location.x,
            'lat': point.location.y,
            'vulnerability': level,
            'slope_pct': slope,
            'ndvi': ndvi,
            'smap': smap,
        })
    return results


def ndvi_timeseries(soil_point_id):
    from soils.models import SoilPointNasaSnapshot
    snapshots = SoilPointNasaSnapshot.objects.filter(
        soil_point_id=soil_point_id,
        product__icontains='NDVI',
    ).order_by('observed_at')
    return [
        {'date': s.observed_at.isoformat(), 'ndvi': s.value}
        for s in snapshots
    ]


def spatial_statistics_by_zone():
    stats = []
    for zone in AdministrativeZone.objects.filter(zone_type='canton'):
        points = SoilPoint.objects.filter(zone=zone, is_validated=True)
        stats.append({
            'zone_code': zone.code,
            'zone_name': zone.name,
            'point_count': points.count(),
            'avg_ph': round(points.aggregate(v=Avg('ph'))['v'] or 0, 2),
            'avg_ndvi': round(points.aggregate(v=Avg('ndvi_3m_avg'))['v'] or 0, 3),
        })
    degraded = AdministrativeZone.objects.filter(zone_type='degraded')
    total_area = 0
    for z in degraded:
        z3857 = z.geometry.transform(3857, clone=True)
        total_area += z3857.area
    return {
        'by_canton': stats,
        'degraded_surface_m2': round(total_area, 2),
        'degraded_surface_ha': round(total_area / 10000, 4),
    }


def smap_correlation():
    """R² between field humidity and SMAP — target > 0.6."""
    import numpy as np
    pairs = list(
        SoilPoint.objects.filter(
            is_validated=True,
            smap_moisture_avg__isnull=False,
        ).values_list('humidity_pct', 'smap_moisture_avg')
    )
    if len(pairs) < 10:
        return {'r_squared': None, 'sample_size': len(pairs), 'message': 'Données insuffisantes'}
    x = np.array([p[1] * 100 for p in pairs])
    y = np.array([p[0] for p in pairs])
    corr = np.corrcoef(x, y)[0, 1]
    r_squared = float(corr ** 2) if not np.isnan(corr) else None
    return {'r_squared': round(r_squared, 3) if r_squared else None, 'sample_size': len(pairs)}
