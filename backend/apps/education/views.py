import random

from django.utils import timezone
from rest_framework import viewsets
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
from .services import award_badges, weekly_leaderboard


class PedagogicalSheetViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = PedagogicalSheet.objects.all()
    serializer_class = PedagogicalSheetSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]


class QuizStartView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        difficulty = request.data.get('difficulty', 'facile')
        count = int(request.data.get('count', 5))
        qs = QuizQuestion.objects.filter(is_active=True, difficulty=difficulty)
        if difficulty == 'mixte':
            qs = QuizQuestion.objects.filter(is_active=True)
        questions = list(qs)
        if len(questions) < count:
            count = len(questions)
        selected = random.sample(questions, count) if questions else []
        session = QuizSession.objects.create(user=request.user, difficulty=difficulty)
        return Response({
            'session_id': session.id,
            'timer_seconds': 20,
            'questions': QuizQuestionPublicSerializer(selected, many=True).data,
        })


class QuizSubmitAnswerView(APIView):
    permission_classes = [IsAuthenticated]

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
        return Response({'top_10': weekly_leaderboard(10)})


class MyBadgesView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        badges = UserBadge.objects.filter(user=request.user)
        return Response(UserBadgeSerializer(badges, many=True).data)
