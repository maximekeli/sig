"""Tâches asynchrones — géolocalisation à grande échelle."""
from datetime import timedelta

from celery import shared_task
from django.conf import settings
from django.contrib.gis.db.models.functions import Distance
from django.contrib.gis.geos import Point
from django.utils import timezone


@shared_task(bind=True, max_retries=3, default_retry_delay=30)
def record_location_history(self, user_id, lon, lat, accuracy_m=None):
    """
    Enregistre l'historique GPS seulement si déplacement ou délai suffisant
    (évite des milliards de lignes avec 10M d'utilisateurs actifs).
    """
    from accounts.models import UserLocationHistory

    point = Point(float(lon), float(lat), srid=4326)
    min_interval = getattr(settings, 'LOCATION_HISTORY_MIN_INTERVAL_SEC', 120)
    min_distance = getattr(settings, 'LOCATION_HISTORY_MIN_DISTANCE_M', 75)
    cutoff = timezone.now() - timedelta(seconds=min_interval)

    last = (
        UserLocationHistory.objects.filter(user_id=user_id)
        .order_by('-recorded_at')
        .first()
    )
    if last:
        if last.recorded_at >= cutoff:
            dist = (
                UserLocationHistory.objects.filter(pk=last.pk)
                .annotate(d=Distance('location', point))
                .values_list('d', flat=True)
                .first()
            )
            if dist is not None and dist.m < min_distance:
                return {'skipped': True, 'reason': 'too_soon_and_near'}

    UserLocationHistory.objects.create(
        user_id=user_id,
        location=point,
        accuracy_m=accuracy_m,
    )
    return {'skipped': False}


@shared_task
def purge_old_location_history():
    """Supprime l'historique GPS au-delà de la rétention configurée."""
    from accounts.models import UserLocationHistory

    days = getattr(settings, 'LOCATION_HISTORY_RETENTION_DAYS', 90)
    cutoff = timezone.now() - timedelta(days=days)
    deleted, _ = UserLocationHistory.objects.filter(recorded_at__lt=cutoff).delete()
    return {'deleted': deleted, 'retention_days': days}
