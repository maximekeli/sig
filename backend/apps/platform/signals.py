from django.db.models.signals import post_save
from django.dispatch import receiver

from accounts.models import UserLocation


@receiver(post_save, sender=UserLocation)
def save_location_history(sender, instance, **kwargs):
    from accounts.models import UserLocationHistory
    UserLocationHistory.objects.create(
        user=instance.user,
        location=instance.location,
        accuracy_m=instance.accuracy_m,
    )
