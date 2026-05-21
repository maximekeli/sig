import random

from django.http import HttpResponse
from django.views.decorators.clickjacking import xframe_options_sameorigin
from django.utils import timezone
from django.views.decorators.clickjacking import xframe_options_sameorigin
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAuthenticatedOrReadOnly
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import (
    PedagogicalSheet,
    QuizQuestion,
    QuizSession,
    UserBadge,
    UserQuizProfile,
)
from .serializers import (
    PedagogicalSheetSerializer,
    QuizAnswerSerializer,
    QuizQuestionPublicSerializer,
    UserBadgeSerializer,
)
from config.throttling import QuizUserThrottle

from .quiz_cache import get_cached_leaderboard, get_cached_quiz_stats, invalidate_quiz_stats
from .services import award_badges
from .tasks import refresh_leaderboard_cache


def pedagogical_sheet_pdf_response(request, pk):
    """Réponse PDF (inline ou ?download=1)."""
    try:
        sheet = PedagogicalSheet.objects.get(pk=pk)
    except PedagogicalSheet.DoesNotExist:
        return Response({'error': 'Fiche introuvable.'}, status=404)
    try:
        from .pdf_build import build_pedagogical_pdf_bytes
        data = build_pedagogical_pdf_bytes(sheet)
    except Exception as exc:
        return Response(
            {'error': f'Génération PDF impossible : {exc}'},
            status=500,
        )
    safe = sheet.theme.replace('/', '-').replace(' ', '_')
    filename = f'sig-sols-fiche-{safe}.pdf'
    resp = HttpResponse(data, content_type='application/pdf')
    if request.query_params.get('download'):
        resp['Content-Disposition'] = f'attachment; filename="{filename}"'
    else:
        resp['Content-Disposition'] = f'inline; filename="{filename}"'
    return resp


class PedagogicalSheetPdfView(APIView):
    """Route explicite pour le PDF (lecture iframe + téléchargement)."""
    permission_classes = [AllowAny]

    @xframe_options_sameorigin
    def get(self, request, pk):
        return pedagogical_sheet_pdf_response(request, pk)


class PedagogicalSheetViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = PedagogicalSheet.objects.all()
    serializer_class = PedagogicalSheetSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

    @action(detail=True, methods=['get'], url_path='pdf', permission_classes=[AllowAny])
    @xframe_options_sameorigin
    def pdf(self, request, pk=None):
        return pedagogical_sheet_pdf_response(request, pk)


class QuizStatsView(APIView):
    """Nombre de questions disponibles par niveau."""
    permission_classes = [AllowAny]

    def get(self, request):
        return Response(get_cached_quiz_stats())


class QuizStartView(APIView):
    permission_classes = [IsAuthenticated]
    throttle_classes = [QuizUserThrottle]

    def post(self, request):
        difficulty = request.data.get('difficulty', 'facile')
        count = min(int(request.data.get('count', 10)), 100)
        count = max(count, 1)
        qs = QuizQuestion.objects.filter(is_active=True, difficulty=difficulty)
        if difficulty == 'mixte':
            qs = QuizQuestion.objects.filter(is_active=True)
        pks = list(qs.values_list('pk', flat=True).distinct())
        available = len(pks)
        if available < count:
            count = available
        chosen = random.sample(pks, count) if pks else []
        selected = list(QuizQuestion.objects.filter(pk__in=chosen))
        selected.sort(key=lambda q: chosen.index(q.pk))
        session = QuizSession.objects.create(user=request.user, difficulty=difficulty)
        return Response({
            'session_id': session.id,
            'timer_seconds': 20,
            'questions': QuizQuestionPublicSerializer(selected, many=True).data,
            'question_count': len(selected),
            'available_in_pool': available,
            'difficulty': difficulty,
        })


class QuizSubmitAnswerView(APIView):
    permission_classes = [IsAuthenticated]
    throttle_classes = [QuizUserThrottle]

    def post(self, request, session_id):
        serializer = QuizAnswerSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            session = QuizSession.objects.get(pk=session_id, user=request.user)
        except QuizSession.DoesNotExist:
            return Response({'error': 'Session introuvable'}, status=404)
        if session.completed:
            return Response({'error': 'Session terminée'}, status=400)

        q = QuizQuestion.objects.get(pk=serializer.validated_data['question_id'])
        correct = serializer.validated_data['selected_index'] == q.correct_index
        points = q.points if correct else 0
        session.score += points
        session.questions_answered += 1
        session.save()

        profile, _ = UserQuizProfile.objects.get_or_create(user=request.user)
        profile.total_score += points
        if q.is_nasa_topic:
            profile.nasa_questions_total += 1
            if correct:
                profile.nasa_questions_correct += 1
        profile.save()

        return Response({
            'correct': correct,
            'points_earned': points,
            'explanation': q.explanation,
            'session_score': session.score,
        })


class QuizFinishView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, session_id):
        try:
            session = QuizSession.objects.get(pk=session_id, user=request.user)
        except QuizSession.DoesNotExist:
            return Response({'error': 'Session introuvable'}, status=404)
        session.completed = True
        session.finished_at = timezone.now()
        session.save()
        if session.difficulty == 'difficile' and session.score >= 30:
            profile, _ = UserQuizProfile.objects.get_or_create(user=request.user)
            profile.difficult_sessions_passed += 1
            profile.save()
        new_badges = award_badges(request.user)
        refresh_leaderboard_cache.delay()
        invalidate_quiz_stats()
        return Response({
            'final_score': session.score,
            'badges_earned': new_badges,
            'all_badges': UserBadgeSerializer(
                UserBadge.objects.filter(user=request.user), many=True,
            ).data,
        })


class LeaderboardView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        return Response(get_cached_leaderboard())


class QuizShareView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, session_id):
        try:
            session = QuizSession.objects.get(pk=session_id, user=request.user, completed=True)
        except QuizSession.DoesNotExist:
            return Response({'error': 'Session introuvable'}, status=404)
        profile, _ = UserQuizProfile.objects.get_or_create(user=request.user)
        return Response({
            'share_text': (
                f'J\'ai obtenu {session.score} pts au quiz SIG Sols '
                f'({session.difficulty}) — {profile.total_score} pts au total !'
            ),
            'score': session.score,
            'difficulty': session.difficulty,
            'total_score': profile.total_score,
        })


class MyBadgesView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        badges = UserBadge.objects.filter(user=request.user)
        return Response(UserBadgeSerializer(badges, many=True).data)
