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
    """Agrégation SQL — adapté à des millions de sessions quiz."""
    from django.db.models import Sum

    week_start = timezone.now() - timedelta(days=7)
    ranked = (
        QuizSession.objects.filter(started_at__gte=week_start, completed=True)
        .values('user_id')
        .annotate(total=Sum('score'))
        .order_by('-total')[:limit]
    )
    user_ids = [row['user_id'] for row in ranked]
    users = User.objects.filter(pk__in=user_ids).only('id', 'username', 'pseudonym')
    users_by_id = {u.pk: u for u in users}
    result = []
    for row in ranked:
        user = users_by_id.get(row['user_id'])
        if not user:
            continue
        name = user.pseudonym or user.username[:3] + '***'
        result.append({'pseudonym': name, 'score': row['total']})
    return result
