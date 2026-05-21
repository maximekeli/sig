import csv
from io import StringIO

from django.contrib.auth import get_user_model
from django.http import HttpResponse
from django.utils import timezone
from rest_framework.views import APIView

from accounts.permissions import IsAdministrator
from .models import UserActivityEvent

User = get_user_model()


class AdminExportUsersCSVView(APIView):
    permission_classes = [IsAdministrator]

    def get(self, request):
        buf = StringIO()
        writer = csv.writer(buf)
        writer.writerow([
            'id', 'username', 'email', 'role', 'first_name', 'last_name',
            'city', 'region', 'date_joined', 'is_active',
        ])
        for u in User.objects.order_by('id').iterator():
            writer.writerow([
                u.id, u.username, u.email, u.role,
                u.first_name, u.last_name, u.city, u.region,
                u.date_joined.isoformat(), u.is_active,
            ])
        resp = HttpResponse(buf.getvalue(), content_type='text/csv; charset=utf-8')
        resp['Content-Disposition'] = 'attachment; filename="utilisateurs.csv"'
        return resp


class AdminExportActivityCSVView(APIView):
    permission_classes = [IsAdministrator]

    def get(self, request):
        days = int(request.query_params.get('days', 30))
        since = timezone.now() - timezone.timedelta(days=days)
        buf = StringIO()
        writer = csv.writer(buf)
        writer.writerow([
            'id', 'user_id', 'username', 'event_type', 'category',
            'view_name', 'created_at',
        ])
        qs = UserActivityEvent.objects.filter(
            created_at__gte=since,
        ).select_related('user').order_by('-created_at')[:50000]
        for ev in qs.iterator():
            writer.writerow([
                ev.id,
                ev.user_id or '',
                ev.user.username if ev.user_id else '',
                ev.event_type,
                ev.category,
                ev.view_name,
                ev.created_at.isoformat(),
            ])
        resp = HttpResponse(buf.getvalue(), content_type='text/csv; charset=utf-8')
        resp['Content-Disposition'] = f'attachment; filename="activite_{days}j.csv"'
        return resp
