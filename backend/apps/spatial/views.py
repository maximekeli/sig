import json

from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.response import Response
from rest_framework.views import APIView
from soils.serializers import AdministrativeZoneSerializer

from . import services


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
