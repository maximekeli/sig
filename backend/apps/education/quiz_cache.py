from django.conf import settings
from django.core.cache import cache

from education.tasks import LEADERBOARD_CACHE_KEY

QUIZ_STATS_KEY = 'quiz:stats:v1'


def get_cached_leaderboard():
    cached = cache.get(LEADERBOARD_CACHE_KEY)
    if cached is not None:
        return cached
    from education.services import weekly_leaderboard
    data = {'top_10': weekly_leaderboard(10)}
    cache.set(LEADERBOARD_CACHE_KEY, data, getattr(settings, 'LEADERBOARD_CACHE_SECONDS', 60))
    return data


def get_cached_quiz_stats():
    cached = cache.get(QUIZ_STATS_KEY)
    if cached is not None:
        return cached
    from education.models import QuizQuestion
    levels = ('facile', 'moyen', 'difficile')
    by_level = {
        d: QuizQuestion.objects.filter(is_active=True, difficulty=d).count()
        for d in levels
    }
    data = {
        'by_level': by_level,
        'total': QuizQuestion.objects.filter(is_active=True).count(),
        'per_level_target': 100,
        'session_options': [5, 10, 15, 20, 30, 50, 100],
    }
    cache.set(QUIZ_STATS_KEY, data, getattr(settings, 'QUIZ_STATS_CACHE_SECONDS', 3600))
    return data


def invalidate_quiz_stats():
    cache.delete(QUIZ_STATS_KEY)
