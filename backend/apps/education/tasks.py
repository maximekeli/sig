"""Tâches quiz / classement — cache pour forte charge."""
from celery import shared_task
from django.conf import settings
from django.core.cache import cache

LEADERBOARD_CACHE_KEY = 'quiz:leaderboard:weekly'


@shared_task
def refresh_leaderboard_cache():
    from education.services import weekly_leaderboard

    data = {'top_10': weekly_leaderboard(10)}
    ttl = getattr(settings, 'LEADERBOARD_CACHE_SECONDS', 60)
    cache.set(LEADERBOARD_CACHE_KEY, data, ttl)
    return {'cached': True, 'entries': len(data['top_10'])}
