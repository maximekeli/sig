from celery import shared_task
from django.conf import settings

from soils.models import SoilPoint

from .pipeline import train_and_save


@shared_task
def check_retrain_fertility_model():
    from .models import FertilityModelRun
    last = FertilityModelRun.objects.filter(is_active=True).first()
    new_points = SoilPoint.objects.filter(is_validated=True).count()
    if not last or new_points >= settings.ML_RETRAIN_NEW_SAMPLES:
        return train_and_save()
    return {'skipped': True, 'reason': 'Threshold not met'}
