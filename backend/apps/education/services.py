from datetime import timedelta

from django.utils import timezone

from accounts.models import User
from .models import QuizSession, UserBadge, UserQuizProfile


def award_badges(user):
    profile, _ = UserQuizProfile.objects.get_or_create(user=user)
    earned = []
    sessions = QuizSession.objects.filter(user=user, completed=True)
    if sessions.filter(questions_answered__gte=5).exists():
        badge, created = UserBadge.objects.get_or_create(
            user=user, badge=UserBadge.BadgeType.APPRENTI,
        )
        if created:
            earned.append(badge.badge)
    if profile.total_score >= 100:
        badge, created = UserBadge.objects.get_or_create(
            user=user, badge=UserBadge.BadgeType.CONNAISSEUR,
        )
        if created:
            earned.append(badge.badge)
    if profile.total_score >= 300 and profile.difficult_sessions_passed >= 3:
        badge, created = UserBadge.objects.get_or_create(
            user=user, badge=UserBadge.BadgeType.EXPERT,
        )
        if created:
            earned.append(badge.badge)
    if profile.nasa_questions_total > 0 and profile.nasa_questions_correct >= profile.nasa_questions_total:
        badge, created = UserBadge.objects.get_or_create(
            user=user, badge=UserBadge.BadgeType.NASA_CHAMPION,
        )
        if created:
            earned.append(badge.badge)
    return earned


def weekly_leaderboard(limit=10):
    week_start = timezone.now() - timedelta(days=7)
    scores = {}
    for session in QuizSession.objects.filter(started_at__gte=week_start, completed=True):
        uid = session.user.pk
        scores[uid] = scores.get(uid, 0) + session.score
    ranked = sorted(scores.items(), key=lambda x: -x[1])[:limit]
    result = []
    for uid, score in ranked:
        user = User.objects.get(pk=uid)
        name = user.pseudonym or user.username[:3] + '***'
        result.append({'pseudonym': name, 'score': score})
    return result
