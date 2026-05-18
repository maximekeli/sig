"""Services de géolocalisation utilisateur en temps réel."""
from datetime import timedelta

from django.conf import settings
from django.contrib.gis.geos import Point
from django.utils import timezone

from .models import UserLocation


def _in_maritime_bbox(lon: float, lat: float) -> bool:
    min_lon, min_lat, max_lon, max_lat = settings.REGION_MARITIME_BBOX
    return min_lon <= lon <= max_lon and min_lat <= lat <= max_lat


def upsert_user_location(
    user,
    lon: float,
    lat: float,
    *,
    accuracy_m: float | None = None,
    heading: float | None = None,
    is_sharing: bool = True,
) -> UserLocation:
    if not _in_maritime_bbox(lon, lat):
        raise ValueError('Position hors de la zone pilote Maritime Togo.')
    point = Point(float(lon), float(lat), srid=4326)
    loc, _ = UserLocation.objects.update_or_create(
        user=user,
        defaults={
            'location': point,
            'accuracy_m': accuracy_m,
            'heading': heading,
            'is_sharing': is_sharing,
        },
    )
    return loc


def list_live_locations(*, exclude_user=None):
    stale = getattr(settings, 'LOCATION_STALE_MINUTES', 5)
    cutoff = timezone.now() - timedelta(minutes=stale)
    qs = (
        UserLocation.objects.filter(is_sharing=True, updated_at__gte=cutoff)
        .select_related('user')
        .order_by('-updated_at')
    )
    if exclude_user:
        qs = qs.exclude(user=exclude_user)
    return qs
