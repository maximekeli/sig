"""Fonctionnalités étendues — recherche, dashboard, modération, rapports."""
import csv
import json
from datetime import timedelta
from io import StringIO

from django.contrib.auth import get_user_model
from django.db.models import Count, Q
from django.http import HttpResponse
from django.utils import timezone
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from accounts.permissions import IsAdministrator
from accounts.social_models import UserFollow
from education.models import PedagogicalSheet, QuizSession, UserBadge
from sig_platform.models import AuditLog, DroughtAlert, Notification
from sig_platform.serializers import AuditLogSerializer, NotificationSerializer
from soils.models import SoilPoint
from videos.models import VideoComment, VideoPost

User = get_user_model()


class NotificationUnreadCountView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        n = Notification.objects.filter(user=request.user, is_read=False).count()
        return Response({'unread_count': n, 'count': n})


class NotificationMarkAllReadView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        updated = Notification.objects.filter(
            user=request.user, is_read=False,
        ).update(is_read=True)
        return Response({'marked': updated})


class GlobalSearchView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        q = (request.query_params.get('q') or '').strip()
        if len(q) < 2:
            return Response({'query': q, 'results': []})
        results = []
        for p in SoilPoint.objects.filter(
            Q(soil_type__icontains=q) | Q(notes__icontains=q),
            validation_status=SoilPoint.ValidationStatus.VALIDATED,
        )[:8]:
            results.append({
                'type': 'point',
                'id': p.id,
                'title': f'Point #{p.id} — {p.soil_type}',
                'subtitle': f'pH {p.ph}',
                'link': '/?view=map',
            })
        for s in PedagogicalSheet.objects.filter(
            Q(title__icontains=q) | Q(content_fr__icontains=q),
        )[:6]:
            results.append({
                'type': 'sheet',
                'id': s.id,
                'title': s.title,
                'subtitle': s.get_theme_display(),
                'link': '/?view=sheets',
            })
        for v in VideoPost.objects.filter(
            status=VideoPost.Status.PUBLISHED,
        ).filter(Q(title__icontains=q) | Q(description__icontains=q) | Q(tags__icontains=q))[:6]:
            results.append({
                'type': 'video',
                'id': v.id,
                'title': v.title,
                'subtitle': v.get_kind_display(),
                'link': f'/?view=videos&video={v.id}',
            })
        for u in User.objects.filter(
            Q(username__icontains=q)
            | Q(first_name__icontains=q)
            | Q(last_name__icontains=q),
            is_active=True,
        )[:6]:
            results.append({
                'type': 'user',
                'id': u.id,
                'title': u.get_full_name() or u.username,
                'subtitle': f'@{u.username}',
                'link': f'/?view=community&user={u.username}',
            })
        return Response({'query': q, 'results': results})


class PersonalDashboardView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        videos = VideoPost.objects.filter(author=user)
        sessions = QuizSession.objects.filter(user=user, completed=True)
        return Response({
            'profile': {
                'username': user.username,
                'display_name': user.get_full_name() or user.username,
            },
            'soil_points_submitted': SoilPoint.objects.filter(created_by=user).count(),
            'videos': {
                'published': videos.filter(status=VideoPost.Status.PUBLISHED).count(),
                'pending': videos.filter(status=VideoPost.Status.PENDING).count(),
            },
            'quiz': {
                'sessions_completed': sessions.count(),
                'best_score': sessions.order_by('-score').values_list('score', flat=True).first() or 0,
                'badges': list(
                    UserBadge.objects.filter(user=user).values_list('badge', flat=True),
                ),
            },
            'social': {
                'followers': UserFollow.objects.filter(following=user).count(),
                'following': UserFollow.objects.filter(follower=user).count(),
            },
            'notifications_unread': Notification.objects.filter(
                user=user, is_read=False,
            ).count(),
        })


class ModerationJournalView(APIView):
    permission_classes = [IsAdministrator]

    def get(self, request):
        items = []
        for v in VideoPost.objects.filter(status=VideoPost.Status.PENDING).select_related('author')[:20]:
            items.append({
                'kind': 'video',
                'id': v.id,
                'title': v.title,
                'author': v.author.username,
                'created_at': v.created_at,
            })
        for c in VideoComment.objects.filter(is_hidden=False).select_related('author', 'post')[:30]:
            items.append({
                'kind': 'comment',
                'id': c.id,
                'title': (c.text or '')[:80],
                'author': c.author.username,
                'post_id': c.post_id,
                'created_at': c.created_at,
            })
        for p in SoilPoint.objects.filter(
            validation_status=SoilPoint.ValidationStatus.PENDING,
        )[:20]:
            items.append({
                'kind': 'soil_point',
                'id': p.id,
                'title': f'Point pH {p.ph}',
                'author': p.created_by.username if p.created_by_id else '—',
                'created_at': p.created_at,
            })
        items.sort(key=lambda x: x['created_at'], reverse=True)
        return Response({'results': items[:50]})


class MinistryReportView(APIView):
    permission_classes = [IsAdministrator]

    def get(self, request):
        since = timezone.now() - timedelta(days=30)
        region = request.query_params.get('region', 'Maritime')
        users = User.objects.filter(region__icontains=region, is_active=True).count()
        points = SoilPoint.objects.filter(
            created_at__gte=since,
            validation_status=SoilPoint.ValidationStatus.VALIDATED,
        ).count()
        videos = VideoPost.objects.filter(
            created_at__gte=since,
            status=VideoPost.Status.PUBLISHED,
        ).count()
        quizzes = QuizSession.objects.filter(started_at__gte=since, completed=True).count()
        alerts = DroughtAlert.objects.filter(is_active=True).count()
        html = f"""<!DOCTYPE html><html lang="fr"><head><meta charset="utf-8"/>
        <title>Rapport SIG Sols — {region}</title>
        <style>body{{font-family:system-ui;max-width:720px;margin:2rem auto;padding:1rem}}
        h1{{color:#134e2a}} table{{width:100%;border-collapse:collapse}}
        td,th{{border:1px solid #ddd;padding:0.5rem}}</style></head><body>
        <h1>Rapport mensuel — Région {region}</h1>
        <p>Période : 30 derniers jours · Généré {timezone.now().strftime('%d/%m/%Y %H:%M')}</p>
        <table><tr><th>Indicateur</th><th>Valeur</th></tr>
        <tr><td>Utilisateurs actifs ({region})</td><td>{users}</td></tr>
        <tr><td>Points sol validés</td><td>{points}</td></tr>
        <tr><td>Vidéos publiées</td><td>{videos}</td></tr>
        <tr><td>Quiz terminés</td><td>{quizzes}</td></tr>
        <tr><td>Alertes sécheresse actives</td><td>{alerts}</td></tr>
        </table><p>DISIA / DUSOL — SIG-SOLS-TOGO-2026-01</p></body></html>"""
        return HttpResponse(html, content_type='text/html; charset=utf-8')


class BulkUserImportView(APIView):
    permission_classes = [IsAdministrator]

    def post(self, request):
        file = request.FILES.get('file')
        if not file:
            raw = request.data.get('csv', '')
            if not raw:
                return Response({'detail': 'Fichier CSV requis.'}, status=400)
            lines = raw.strip().splitlines()
        else:
            lines = file.read().decode('utf-8', errors='replace').splitlines()
        reader = csv.DictReader(lines)
        created = 0
        errors = []
        for i, row in enumerate(reader, start=2):
            username = (row.get('username') or '').strip()
            password = (row.get('password') or 'ChangeMe123!').strip()
            if not username:
                errors.append(f'Ligne {i}: username manquant')
                continue
            if User.objects.filter(username=username).exists():
                continue
            try:
                User.objects.create_user(
                    username=username,
                    password=password,
                    email=row.get('email', ''),
                    role=row.get('role', User.Role.PUBLIC),
                    first_name=row.get('first_name', ''),
                    last_name=row.get('last_name', ''),
                    region=row.get('region', 'Maritime'),
                )
                created += 1
            except Exception as exc:
                errors.append(f'{username}: {exc}')
        return Response({'created': created, 'errors': errors[:20]})


class AlertsNearMeView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            lat = float(request.query_params.get('lat'))
            lon = float(request.query_params.get('lon'))
        except (TypeError, ValueError):
            return Response({'detail': 'lat et lon requis.'}, status=400)
        radius_km = float(request.query_params.get('radius_km', 25))
        alerts = DroughtAlert.objects.filter(is_active=True).select_related(
            'zone', 'soil_point',
        )[:50]
        results = []
        for a in alerts:
            pt = a.soil_point
            if pt and pt.location:
                dlat = abs(pt.location.y - lat)
                dlon = abs(pt.location.x - lon)
                approx_km = (dlat ** 2 + dlon ** 2) ** 0.5 * 111
                if approx_km <= radius_km:
                    results.append({
                        'id': a.id,
                        'message': a.message,
                        'severity': a.severity,
                        'distance_km': round(approx_km, 1),
                    })
        return Response({'alerts': results, 'count': len(results)})
