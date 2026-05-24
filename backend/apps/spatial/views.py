import json

from rest_framework.permissions import AllowAny, IsAuthenticatedOrReadOnly
from rest_framework.response import Response
from rest_framework.views import APIView
from soils.models import AdministrativeZone
from soils.serializers import AdministrativeZoneSerializer

from . import services


def _parse_bool_flag(value, *, default=True):
    """Interprète un flag JSON/query (true/false/1/0) ; absent → default."""
    if value is None:
        return default
    if isinstance(value, bool):
        return value
    if isinstance(value, (int, float)):
        return bool(value)
    if isinstance(value, str):
        return value.strip().lower() in ('1', 'true', 'yes', 'on')
    return bool(value)


class ProximityView(APIView):
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get(self, request):
        lon = request.query_params.get('lon')
        lat = request.query_params.get('lat')
        radius = request.query_params.get('radius_m', '1000')
        if not lon or not lat:
            return Response({'error': 'lon et lat requis'}, status=400)
        radius_m = max(100, min(int(radius), 10000))
        data = services.proximity_search(lon, lat, radius_m)
        return Response({'results': data, 'count': len(data)})


class IntersectionView(APIView):
    permission_classes = [IsAuthenticatedOrReadOnly]

    def post(self, request):
        geom = request.data.get('geometry')
        if not geom:
            return Response({'error': 'geometry (GeoJSON) requis'}, status=400)
        zones = services.intersection_zones(json.dumps(geom))
        serializer = AdministrativeZoneSerializer(zones, many=True)
        return Response({'zones': serializer.data, 'count': zones.count()})


class BufferView(APIView):
    permission_classes = [IsAuthenticatedOrReadOnly]

    def post(self, request):
        geom = request.data.get('geometry')
        distance_m = request.data.get('distance_m', 500)
        if not geom:
            return Response({'error': 'geometry requis'}, status=400)
        result = services.buffer_geometry(json.dumps(geom), distance_m)
        return Response({'buffer': json.loads(result)})


class AreaView(APIView):
    permission_classes = [IsAuthenticatedOrReadOnly]

    def post(self, request):
        geom = request.data.get('geometry')
        if not geom:
            return Response({'error': 'geometry requis'}, status=400)
        return Response(services.polygon_area(json.dumps(geom)))


class VulnerabilityZoningView(APIView):
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get(self, request):
        data = services.vulnerability_zoning()
        return Response({'points': data[:500], 'total': len(data)})


class NdviTimeseriesView(APIView):
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get(self, request, point_id):
        series = services.ndvi_timeseries(point_id)
        return Response({'soil_point_id': point_id, 'series': series})


class SpatialStatisticsView(APIView):
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get(self, request):
        return Response(services.spatial_statistics_by_zone())


class SmapCorrelationView(APIView):
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get(self, request):
        return Response(services.smap_correlation())


class ParcelAnalyzeView(APIView):
    """
    Analyse automatique d'une parcelle (polygone GeoJSON ou zone administrative).
    NASA (NDVI, SMAP) + IA fertilité + vulnérabilité.
    """
    # POST utilisé pour géométrie dessinée : doit rester utilisable sans compte (démonstration publique).
    permission_classes = [AllowAny]

    def post(self, request):
        from .parcel_analysis import analyze_parcel

        use_ml = _parse_bool_flag(request.data.get('use_ml'), default=True)
        use_sentinel = _parse_bool_flag(request.data.get('use_sentinel'), default=True)
        use_weather = _parse_bool_flag(request.data.get('use_weather'), default=True)
        try:
            result = analyze_parcel(
                geometry=request.data.get('geometry'),
                zone_code=request.data.get('zone_code'),
                zone_id=request.data.get('zone_id'),
                use_ml=use_ml,
                use_sentinel=use_sentinel,
                use_weather=use_weather,
            )
        except ValueError as exc:
            return Response({'error': str(exc)}, status=400)
        return Response(result)


class ParcelZonesListView(APIView):
    """Liste des zones sélectionnables (cantons, parcelles dégradées)."""
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get(self, request):
        zone_type = request.query_params.get('zone_type', 'canton')
        qs = AdministrativeZone.objects.filter(zone_type=zone_type).order_by('name')
        data = [
            {
                'id': z.id,
                'code': z.code,
                'name': z.name,
                'zone_type': z.zone_type,
            }
            for z in qs[:200]
        ]
        return Response({'zones': data, 'count': len(data)})


class ParcelZonesGeoJsonView(APIView):
    """GeoJSON des parcelles / zones pour affichage et sélection sur la carte."""

    permission_classes = [IsAuthenticatedOrReadOnly]

    def get(self, request):
        from soils.serializers import AdministrativeZoneSerializer

        types_param = request.query_params.get('types', 'canton,degraded')
        types = [t.strip() for t in types_param.split(',') if t.strip()]
        qs = AdministrativeZone.objects.filter(zone_type__in=types).order_by('name')
        data = AdministrativeZoneSerializer(qs, many=True).data
        if isinstance(data, list):
            return Response({'type': 'FeatureCollection', 'features': data})
        return Response(data)


class ParcelLiveView(APIView):
    """Analyse parcelle en temps réel (léger par défaut : sans IA). GET zone_code ou POST geometry."""

    permission_classes = [AllowAny]

    def get(self, request):
        from .parcel_analysis import analyze_parcel

        zone_code = request.query_params.get('zone_code')
        if not zone_code:
            return Response({'error': 'zone_code requis'}, status=400)
        use_ml = request.query_params.get('use_ml', '0') == '1'
        use_sentinel = request.query_params.get('use_sentinel', '0') == '1'
        use_weather = request.query_params.get('use_weather', '0') == '1'
        try:
            return Response(analyze_parcel(
                zone_code=zone_code,
                use_ml=use_ml,
                use_sentinel=use_sentinel,
                use_weather=use_weather,
            ))
        except ValueError as exc:
            return Response({'error': str(exc)}, status=400)

    def post(self, request):
        from .parcel_analysis import analyze_parcel

        use_ml = _parse_bool_flag(request.data.get('use_ml'), default=False)
        use_sentinel = _parse_bool_flag(request.data.get('use_sentinel'), default=True)
        use_weather = _parse_bool_flag(request.data.get('use_weather'), default=True)
        try:
            return Response(analyze_parcel(
                geometry=request.data.get('geometry'),
                zone_code=request.data.get('zone_code'),
                zone_id=request.data.get('zone_id'),
                use_ml=use_ml,
                use_sentinel=use_sentinel,
                use_weather=use_weather,
            ))
        except ValueError as exc:
            return Response({'error': str(exc)}, status=400)
