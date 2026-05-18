import csv
import json

from django.contrib.gis.geos import GEOSGeometry
from django.db.models import Avg, Count
from django.http import HttpResponse
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.response import Response
from rest_framework.views import APIView

from accounts.permissions import IsAgentOrAdmin, IsAdministrator
from platform.audit import log_action

from .filters import SoilPointFilter
from .models import AdministrativeZone, SoilPoint
from .serializers import (
    AdministrativeZoneSerializer,
    SoilPointListSerializer,
    SoilPointSerializer,
)


class SoilPointViewSet(viewsets.ModelViewSet):
    queryset = SoilPoint.objects.select_related('zone').all()
    permission_classes = [IsAuthenticatedOrReadOnly]
    filterset_class = SoilPointFilter
    search_fields = ['notes', 'source', 'producer']

    def get_serializer_class(self):
        if self.action == 'list' and self.request.query_params.get('light') == '1':
            return SoilPointListSerializer
        return SoilPointSerializer

    def perform_create(self, serializer):
        user = self.request.user if self.request.user.is_authenticated else None
        data = self.request.data
        parent_id = data.get('parent_point')
        props = data.get('properties') if isinstance(data.get('properties'), dict) else {}
        if not parent_id and props:
            parent_id = props.get('parent_point')
        extra = {}
        if parent_id:
            extra['parent_point_id'] = parent_id
        point = serializer.save(created_by=user, **extra)
        if user:
            log_action(user, 'create', 'SoilPoint', point.pk)

    @action(detail=True, methods=['post'], permission_classes=[IsAdministrator])
    def validate_point(self, request, pk=None):
        point = self.get_object()
        action = request.data.get('action', 'validate')
        if action == 'reject':
            point.validation_status = SoilPoint.ValidationStatus.REJECTED
            point.is_validated = False
        else:
            point.validation_status = SoilPoint.ValidationStatus.VALIDATED
            point.is_validated = True
        from django.utils import timezone
        point.validated_by = request.user
        point.validated_at = timezone.now()
        point.save()
        log_action(request.user, 'validate', 'SoilPoint', point.pk, {'action': action})
        return Response({'validation_status': point.validation_status})

    @action(detail=True, methods=['get'])
    def predict_fertility(self, request, pk=None):
        from ml_predict.pipeline import predict_fertility
        point = self.get_object()
        result = predict_fertility({
            'ph': point.ph,
            'humidity_pct': point.humidity_pct,
            'soil_type': point.soil_type,
            'ndvi_3m_avg': point.ndvi_3m_avg,
            'smap_moisture_avg': point.smap_moisture_avg,
            'slope_pct': point.slope_pct,
            'elevation_m': point.elevation_m,
        })
        return Response(result)

    @action(detail=False, methods=['get'], url_path='geojson')
    def export_geojson(self, request):
        qs = self.filter_queryset(self.get_queryset())
        serializer = SoilPointSerializer(qs[:2000], many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'], url_path='export-csv')
    def export_csv(self, request):
        qs = self.filter_queryset(self.get_queryset())
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="soil_points.csv"'
        writer = csv.writer(response)
        writer.writerow([
            'id', 'lon', 'lat', 'ph', 'humidity_pct', 'soil_type',
            'fertility_class', 'collected_at', 'source',
        ])
        for p in qs.iterator():
            writer.writerow([
                p.id, p.location.x, p.location.y, p.ph, p.humidity_pct,
                p.soil_type, p.fertility_class, p.collected_at, p.source,
            ])
        return response

    @action(detail=False, methods=['post'], parser_classes=[MultiPartParser, FormParser],
            permission_classes=[IsAgentOrAdmin])
    def import_data(self, request):
        """Import GeoJSON or CSV (Agent/Admin)."""
        upload = request.FILES.get('file')
        if not upload:
            return Response({'error': 'Fichier requis.'}, status=400)
        name = upload.name.lower()
        created = 0
        if name.endswith('.geojson') or name.endswith('.json'):
            data = json.load(upload)
            for feat in data.get('features', []):
                geom = GEOSGeometry(json.dumps(feat['geometry']), srid=4326)
                props = feat.get('properties', {})
                SoilPoint.objects.create(
                    location=geom.centroid if geom.geom_type != 'Point' else geom,
                    ph=float(props.get('ph', 6.0)),
                    humidity_pct=float(props.get('humidity_pct', 30)),
                    soil_type=props.get('soil_type', 'limoneux'),
                    collected_at=props.get('collected_at', '2025-01-01'),
                    source=props.get('source', 'import'),
                )
                created += 1
        else:
            return Response({'error': 'Format non supporté (GeoJSON).'}, status=400)
        return Response({'created': created})


class AdministrativeZoneViewSet(viewsets.ModelViewSet):
    queryset = AdministrativeZone.objects.all()
    serializer_class = AdministrativeZoneSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    filterset_fields = ['zone_type', 'code']


class DashboardStatsView(APIView):
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get(self, request):
        points = SoilPoint.objects.filter(is_validated=True)
        zones = AdministrativeZone.objects.filter(zone_type='degraded')
        return Response({
            'total_points': points.count(),
            'avg_ph': round(points.aggregate(v=Avg('ph'))['v'] or 0, 2),
            'avg_humidity': round(points.aggregate(v=Avg('humidity_pct'))['v'] or 0, 2),
            'avg_ndvi': round(points.aggregate(v=Avg('ndvi_3m_avg'))['v'] or 0, 3),
            'by_soil_type': list(
                points.values('soil_type').annotate(count=Count('id')).order_by('-count')
            ),
            'degraded_zones_count': zones.count(),
            'fertility_distribution': list(
                points.exclude(fertility_class='').values('fertility_class')
                .annotate(count=Count('id'))
            ),
        })
