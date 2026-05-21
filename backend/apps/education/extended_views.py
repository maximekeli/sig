from django.utils import timezone
from .certificate_pdf import certificate_verify_token
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import PedagogicalSheet, QuizSession, UserBadge


class LearningPathView(APIView):
    """Parcours : fiches → quiz → badge → certificat."""

    permission_classes = [IsAuthenticated]

    def get(self, request):
        sheets = list(PedagogicalSheet.objects.order_by('order').values('id', 'title', 'theme'))
        completed_sessions = QuizSession.objects.filter(
            user=request.user, completed=True,
        ).count()
        badges = list(
            UserBadge.objects.filter(user=request.user).values_list('badge', flat=True),
        )
        steps = []
        for i, s in enumerate(sheets):
            steps.append({
                'order': i + 1,
                'type': 'sheet',
                'sheet_id': s['id'],
                'title': s['title'],
                'done': True,
            })
        steps.append({
            'order': len(steps) + 1,
            'type': 'quiz',
            'title': 'Quiz pédagogique (≥ 1 session)',
            'done': completed_sessions >= 1,
        })
        steps.append({
            'order': len(steps) + 1,
            'type': 'badge',
            'title': 'Obtenir un badge',
            'done': len(badges) >= 1,
        })
        steps.append({
            'order': len(steps) + 1,
            'type': 'certificate',
            'title': 'Certificat (score ≥ 10)',
            'done': QuizSession.objects.filter(
                user=request.user, completed=True, score__gte=10,
            ).exists(),
        })
        progress = sum(1 for s in steps if s['done']) / max(len(steps), 1) * 100
        return Response({
            'steps': steps,
            'progress_percent': round(progress, 1),
            'badges': badges,
        })


class WeeklyChallengeView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        week = timezone.now().isocalendar()[1]
        best = QuizSession.objects.filter(
            user=request.user,
            completed=True,
            started_at__week=week,
        ).order_by('-score').first()
        return Response({
            'week': week,
            'challenge': 'Terminez 3 quiz cette semaine avec un score total ≥ 50',
            'sessions_this_week': QuizSession.objects.filter(
                user=request.user,
                completed=True,
                started_at__week=week,
            ).count(),
            'best_score_this_week': best.score if best else 0,
            'target_sessions': 3,
            'target_score': 50,
        })


class CertificateVerifyView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, token):
        try:
            session_id = int(token.split('-')[0])
        except (ValueError, IndexError):
            return Response({'valid': False, 'detail': 'Token invalide.'})
        try:
            session = QuizSession.objects.get(pk=session_id, completed=True)
        except QuizSession.DoesNotExist:
            return Response({'valid': False})
        valid = token == certificate_verify_token(session)
        return Response({
            'valid': valid and session.score >= 10,
            'username': session.user.username,
            'score': session.score,
            'finished_at': session.finished_at,
        })
