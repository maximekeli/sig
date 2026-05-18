"""Vues étendues : validation, notes, heatmap, comparaison."""
from django.db.models import Avg
from django.utils import timezone
from rest_framework import status, viewsets
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from rest_framework.response import Response
from rest_framework.views import APIView

from accounts.permissions import IsAdministrator, IsAgentOrAdmin
from platform.audit import log_action

from .models import SoilPoint, SoilPointNote
from .serializers_notes import SoilPointNoteSerializer


class SoilPointNoteViewSet(viewsets.ModelViewSet):
    serializer_class = SoilPointNoteSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        qs = SoilPointNote.objects.select_related('author', 'soil_point')
        point_id = self.request.query_params.get('soil_point')
        if point_id:
            qs = qs.filter(soil_point_id=point_id)
        return qs.order_by('created_at')

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)


class SoilPointValidateView(APIView):
    permission_classes = [IsAdministrator]

    def post(self, request, pk):
        point = SoilPoint.objects.filter(pk=pk).first()
        if not point:
            return Response({'error': 'Point introuvable'}, status=404)
        action = request.data.get('action', 'validate')
        if action == 'reject':
            point.validation_status = SoilPoint.ValidationStatus.REJECTED
            point.is_validated = False
        else:
            point.validation_status = SoilPoint.ValidationStatus.VALIDATED
            point.is_validated = True
        point.validated_by = request.user
        point.validated_at = timezone.now()
        point.save()
        log_action(request.user, 'validate', 'SoilPoint', point.pk, {'action': action})
        return Response({'id': point.id, 'validation_status': point.validation_status})


class SoilPointCompareView(APIView):
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get(self, request, pk):
        point = SoilPoint.objects.filter(pk=pk).first()
        if not point:
            return Response({'error': 'Point introuvable'}, status=404)
        follow_ups = SoilPoint.objects.filter(parent_point=point).order_by('collected_at')
        history = list(
            SoilPoint.objects.filter(pk=point.pk).values(
                'id', 'ph', 'humidity_pct', 'ndvi_3m_avg', 'collected_at', 'validation_status',
            ),
        ) + list(follow_ups.values(
            'id', 'ph', 'humidity_pct', 'ndvi_3m_avg', 'collected_at', 'validation_status',
        ))
        return Response({'point_id': pk, 'history': history})


class HeatmapDataView(APIView):
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get(self, request):
        field = request.query_params.get('field', 'ph')
        allowed = {'ph', 'humidity_pct', 'ndvi_3m_avg', 'fertility_score'}
        if field not in allowed:
            field = 'ph'
        points = SoilPoint.objects.filter(is_validated=True).exclude(
            **{f'{field}__isnull': True},
        )[:2000]
        data = [
            [p.location.y, p.location.x, getattr(p, field) or 0]
            for p in points
        ]
        return Response({'field': field, 'points': data})


class PendingValidationView(APIView):
    permission_classes = [IsAdministrator]

    def get(self, request):
        qs = SoilPoint.objects.filter(
            validation_status=SoilPoint.ValidationStatus.PENDING,
        ).order_by('-created_at')[:100]
        from .serializers import SoilPointListSerializer
        return Response({
            'count': qs.count(),
            'results': SoilPointListSerializer(qs, many=True).data,
        })
