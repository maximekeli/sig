from celery import shared_task
from django.contrib.auth import get_user_model
from django.db.models import Q

from soils.models import SoilPoint

User = get_user_model()


@shared_task
def check_drought_alerts():
    """Détecte points à NDVI bas ou SMAP bas et crée alertes + notifications."""
    from platform.models import DroughtAlert, Notification

    created = 0
    agents = User.objects.filter(role__in=['agent', 'admin'], is_active=True)
    at_risk = SoilPoint.objects.filter(is_validated=True).filter(
        Q(ndvi_3m_avg__lt=0.3) | Q(smap_moisture_avg__lt=0.15),
    )[:50]

    for point in at_risk:
        ndvi = point.ndvi_3m_avg or 0.5
        smap = point.smap_moisture_avg or 0.25
        if ndvi >= 0.3 and smap >= 0.15:
            continue
        if DroughtAlert.objects.filter(soil_point=point, is_active=True).exists():
            continue
        alert = DroughtAlert.objects.create(
            soil_point=point,
            ndvi=ndvi,
            smap=smap,
            severity='elevee' if ndvi < 0.25 else 'moyenne',
            message=(
                f'Point #{point.id}: stress hydrique '
                f'(NDVI={ndvi:.2f}, SMAP={smap:.2f})'
            ),
        )
        created += 1
        for agent in agents:
            Notification.objects.create(
                user=agent,
                title='Alerte sécheresse',
                message=alert.message,
                level=Notification.Level.ALERT,
                link=f'/frontend/index.html#point-{point.id}',
            )
    return {'alerts_created': created}
