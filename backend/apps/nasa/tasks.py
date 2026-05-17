from celery import shared_task

from .ingestion import ingest_all


@shared_task(name='nasa.tasks.ingest_all_nasa_layers')
def ingest_all_nasa_layers():
    return ingest_all()
