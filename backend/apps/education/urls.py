from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    LeaderboardView,
    MyBadgesView,
    PedagogicalSheetPdfView,
    PedagogicalSheetViewSet,
    QuizCertificateView,
    QuizFinishView,
    QuizShareView,
    QuizStartView,
    QuizStatsView,
    QuizSubmitAnswerView,
)

router = DefaultRouter()
router.register('sheets', PedagogicalSheetViewSet, basename='pedagogical-sheets')

urlpatterns = [
    path('sheets/<int:pk>/pdf/', PedagogicalSheetPdfView.as_view(), name='pedagogical-sheet-pdf'),
    path('', include(router.urls)),
    path('quiz/stats/', QuizStatsView.as_view(), name='quiz-stats'),
    path('quiz/start/', QuizStartView.as_view(), name='quiz-start'),
    path('quiz/<int:session_id>/answer/', QuizSubmitAnswerView.as_view(), name='quiz-answer'),
    path('quiz/<int:session_id>/finish/', QuizFinishView.as_view(), name='quiz-finish'),
    path('quiz/leaderboard/', LeaderboardView.as_view(), name='quiz-leaderboard'),
    path('quiz/badges/', MyBadgesView.as_view(), name='quiz-badges'),
    path('quiz/<int:session_id>/share/', QuizShareView.as_view(), name='quiz-share'),
    path(
        'quiz/<int:session_id>/certificate/',
        QuizCertificateView.as_view(),
        name='quiz-certificate',
    ),
]
