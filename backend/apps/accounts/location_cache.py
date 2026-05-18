"""Cache Redis des positions live — réduit la charge DB."""
from django.conf import settings
from django.core.cache import cache

from .cache_keys import LIVE_LOCATIONS_EXCLUDE_KEY, LIVE_LOCATIONS_KEY
from .services import list_live_locations
from .serializers import UserLocationSerializer


def _ttl():
    return getattr(settings, 'LIVE_LOCATIONS_CACHE_SECONDS', 15)


def invalidate_live_locations_cache():
    cache.delete(LIVE_LOCATIONS_KEY)
    try:
        cache.delete_pattern('*live_locations:exclude:*')
    except AttributeError:
        pass


def get_cached_live_locations(*, exclude_user=None):
    if exclude_user is None:
        cached = cache.get(LIVE_LOCATIONS_KEY)
        if cached is not None:
            return cached

        qs = list_live_locations(exclude_user=None)
        payload = {
            'count': qs.count(),
            'stale_minutes': settings.LOCATION_STALE_MINUTES,
            'users': UserLocationSerializer(qs, many=True).data,
        }
        cache.set(LIVE_LOCATIONS_KEY, payload, _ttl())
        return payload

    key = LIVE_LOCATIONS_EXCLUDE_KEY.format(user_id=exclude_user.pk)
    cached = cache.get(key)
    if cached is not None:
        return cached

    qs = list_live_locations(exclude_user=exclude_user)
    payload = {
        'count': qs.count(),
        'stale_minutes': settings.LOCATION_STALE_MINUTES,
        'users': UserLocationSerializer(qs, many=True).data,
    }
    cache.set(key, payload, _ttl())
    return payload
