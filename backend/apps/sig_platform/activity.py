"""Ingestion et agrégations activité utilisateur."""
from datetime import timedelta

from django.contrib.auth import get_user_model
from django.db.models import Count
from django.db.models.functions import TruncDate
from django.utils import timezone

from .models import UserActivityEvent

User = get_user_model()

MAX_BATCH = 100


def ingest_activity_events(user, session_id, events, *, ip=None, user_agent=''):
    """Enregistre un lot d'événements (max MAX_BATCH)."""
    if not session_id or not events:
        return 0
    batch = events[:MAX_BATCH]
    rows = []
    for ev in batch:
        et = str(ev.get('event_type', 'unknown'))[:80]
        cat = ev.get('category', UserActivityEvent.Category.OTHER)
        if cat not in UserActivityEvent.Category.values:
            cat = UserActivityEvent.Category.OTHER
        rows.append(UserActivityEvent(
            user=user if user and user.is_authenticated else None,
            session_id=str(session_id)[:64],
            event_type=et,
            category=cat,
            view_name=str(ev.get('view_name', ''))[:40],
            detail=ev.get('detail') if isinstance(ev.get('detail'), dict) else {},
            ip_address=ip,
            user_agent=(user_agent or '')[:300],
        ))
    UserActivityEvent.objects.bulk_create(rows, batch_size=50)
    return len(rows)


def analytics_summary(days=30):
    """Statistiques agrégées pour admin / data science."""
    since = timezone.now() - timedelta(days=days)
    qs = UserActivityEvent.objects.filter(created_at__gte=since)
    total = qs.count()
    today_start = timezone.now().replace(hour=0, minute=0, second=0, microsecond=0)
    today = qs.filter(created_at__gte=today_start).count()

    by_event = list(
        qs.values('event_type')
        .annotate(count=Count('id'))
        .order_by('-count')[:40],
    )
    by_category = list(
        qs.values('category')
        .annotate(count=Count('id'))
        .order_by('-count'),
    )
    by_view = list(
        qs.exclude(view_name='')
        .values('view_name')
        .annotate(count=Count('id'))
        .order_by('-count')[:20],
    )
    by_day = list(
        qs.annotate(day=TruncDate('created_at'))
        .values('day')
        .annotate(count=Count('id'))
        .order_by('day'),
    )
    top_users = list(
        qs.filter(user__isnull=False)
        .values('user_id', 'user__username')
        .annotate(count=Count('id'))
        .order_by('-count')[:25],
    )

    map_zoom = qs.filter(event_type='map_zoom').count()
    map_pan = qs.filter(event_type='map_pan').count()

    users_by_role = list(
        User.objects.values('role').annotate(count=Count('id')).order_by('-count'),
    )
    age_buckets = {'13-17': 0, '18-25': 0, '26-35': 0, '36-50': 0, '51+': 0, 'unknown': 0}
    for u in User.objects.only('age'):
        a = u.age
        if a is None:
            age_buckets['unknown'] += 1
        elif a < 18:
            age_buckets['13-17'] += 1
        elif a <= 25:
            age_buckets['18-25'] += 1
        elif a <= 35:
            age_buckets['26-35'] += 1
        elif a <= 50:
            age_buckets['36-50'] += 1
        else:
            age_buckets['51+'] += 1

    by_region = list(
        User.objects.exclude(region='')
        .values('region')
        .annotate(count=Count('id'))
        .order_by('-count')[:15],
    )

    return {
        'period_days': days,
        'events_total': total,
        'events_today': today,
        'map_zoom_total': map_zoom,
        'map_pan_total': map_pan,
        'by_event_type': by_event,
        'by_category': by_category,
        'by_view': by_view,
        'by_day': [{'day': str(r['day']), 'count': r['count']} for r in by_day],
        'top_users': [
            {'user_id': r['user_id'], 'username': r['user__username'], 'count': r['count']}
            for r in top_users
        ],
        'users_total': User.objects.count(),
        'users_by_role': users_by_role,
        'age_distribution': age_buckets,
        'users_by_region': by_region,
    }


def user_activity_summary(user_id, days=90):
    """Résumé + timeline pour un utilisateur."""
    since = timezone.now() - timedelta(days=days)
    qs = UserActivityEvent.objects.filter(user_id=user_id, created_at__gte=since)
    by_type = list(
        qs.values('event_type').annotate(count=Count('id')).order_by('-count'),
    )
    timeline = list(
        qs.order_by('-created_at')[:500].values(
            'id', 'event_type', 'category', 'view_name', 'detail', 'created_at',
        ),
    )
    for row in timeline:
        row['created_at'] = row['created_at'].isoformat() if row['created_at'] else None
    try:
        user = User.objects.get(pk=user_id)
        profile = {
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'age': user.age,
            'role': user.role,
            'region': user.region,
            'city': user.city,
            'date_joined': user.date_joined.isoformat(),
        }
    except User.DoesNotExist:
        profile = None
    return {
        'user': profile,
        'period_days': days,
        'events_total': qs.count(),
        'by_event_type': by_type,
        'timeline': timeline,
    }
