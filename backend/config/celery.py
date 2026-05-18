import os

from celery import Celery
from celery.schedules import crontab

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

app = Celery('sig_sols')  # pyright: ignore[reportCallIssue]
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()

app.conf.beat_schedule = {
    'nasa-weekly-ingestion': {
        'task': 'nasa.tasks.ingest_all_nasa_layers',
        'schedule': crontab(day_of_week=1, hour=2, minute=0),
    },
    'ml-retrain-quarterly-check': {
        'task': 'ml_predict.tasks.check_retrain_fertility_model',
        'schedule': crontab(day_of_month=1, hour=3, minute=0),
    },
}
