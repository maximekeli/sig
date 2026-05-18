from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.http import HttpResponse
from django.template.loader import render_to_string
from django.db.models import Avg
from django.utils import timezone
from rest_framework import generics, status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from accounts.permissions import IsAdministrator
from soils.models import AdministrativeZone, SoilPoint

from .models import AuditLog, DroughtAlert, Notification, PasswordResetToken
from .serializers import (
    AuditLogSerializer,
    DroughtAlertSerializer,
    NotificationSerializer,
    PasswordResetConfirmSerializer,
    PasswordResetRequestSerializer,
)

User = get_user_model()


class AdminDashboardView(APIView):
    permission_classes = [IsAdministrator]

    def get(self, request):
        from accounts.models import UserLocation
        from nasa.models import NasaLayerCatalog
        from ml_predict.models import FertilityModelRun

        return Response({
            'users_total': User.objects.count(),
            'users_active': User.objects.filter(is_active=True).count(),
            'soil_points': SoilPoint.objects.count(),
            'pending_validation': SoilPoint.objects.filter(
                validation_status=SoilPoint.ValidationStatus.PENDING,
            ).count(),
            'live_agents': UserLocation.objects.filter(
                updated_at__gte=timezone.now() - timezone.timedelta(minutes=5),
                is_sharing=True,
            ).count(),
            'nasa_layers': NasaLayerCatalog.objects.count(),
            'active_alerts': DroughtAlert.objects.filter(is_active=True).count(),
            'ml_model': FertilityModelRun.objects.filter(is_active=True).values(
                'algorithm', 'f1_macro', 'trained_at',
            ).first(),
            'recent_audit': AuditLogSerializer(
                AuditLog.objects.all()[:15], many=True,
            ).data,
        })


class NotificationListView(generics.ListAPIView):
    serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Notification.objects.filter(user=self.request.user)[:50]


class NotificationMarkReadView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        n = Notification.objects.filter(user=request.user, pk=pk).first()
        if not n:
            return Response({'error': 'Introuvable'}, status=404)
        n.is_read = True
        n.save(update_fields=['is_read'])
        return Response({'ok': True})


class DroughtAlertListView(generics.ListAPIView):
    queryset = DroughtAlert.objects.filter(is_active=True).select_related(
        'soil_point', 'zone',
    )[:100]
    serializer_class = DroughtAlertSerializer
    permission_classes = [IsAuthenticated]


class AuditLogListView(generics.ListAPIView):
    queryset = AuditLog.objects.select_related('user').all()[:200]
    serializer_class = AuditLogSerializer
    permission_classes = [IsAdministrator]


class PasswordResetRequestView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        ser = PasswordResetRequestSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        email = ser.validated_data['email']
        user = User.objects.filter(email__iexact=email).first()
        if user:
            prt = PasswordResetToken.create_for_user(user)
            reset_url = (
                f'{request.build_absolute_uri("/frontend/reset-password.html")}'
                f'?token={prt.token}'
            )
            send_mail(
                subject='SIG Sols Togo — Réinitialisation mot de passe',
                message=f'Utilisez ce lien (24 h): {reset_url}',
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[user.email],
                fail_silently=True,
            )
        return Response({
            'detail': 'Si un compte existe, un email a été envoyé.',
        })


class PasswordResetConfirmView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        ser = PasswordResetConfirmSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        prt = PasswordResetToken.objects.filter(
            token=ser.validated_data['token'], used=False,
        ).first()
        if not prt or not prt.is_valid():
            return Response({'error': 'Token invalide ou expiré.'}, status=400)
        prt.user.set_password(ser.validated_data['new_password'])
        prt.user.save()
        prt.used = True
        prt.save(update_fields=['used'])
        return Response({'detail': 'Mot de passe réinitialisé.'})


class ZoneReportView(APIView):
    """Rapport HTML zone (impression PDF via navigateur)."""

    permission_classes = [IsAuthenticated]

    def get(self, request, zone_code):
        zone = AdministrativeZone.objects.filter(code=zone_code).first()
        if not zone:
            return Response({'error': 'Zone introuvable'}, status=404)
        points = SoilPoint.objects.filter(zone=zone, is_validated=True)
        html = render_to_string('reports/zone_report.html', {
            'zone': zone,
            'points': points[:500],
            'point_count': points.count(),
            'avg_ph': points.aggregate(v=Avg('ph'))['v'] if points.exists() else None,
            'generated_at': timezone.now(),
        })
        return HttpResponse(html)
