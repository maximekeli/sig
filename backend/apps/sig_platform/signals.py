from django.db.models.signals import post_save
from django.dispatch import receiver

from accounts.models import UserLocation


@receiver(post_save, sender=UserLocation)
def enqueue_location_history(sender, instance, **kwargs):
    """Historique GPS en file Celery (non bloquant, avec anti-surcharge)."""
    from accounts.tasks import record_location_history

    lon, lat = instance.location.x, instance.location.y
    record_location_history.delay(
        instance.user_id,
        lon,
        lat,
        instance.accuracy_m,
    )
