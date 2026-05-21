"""Limite globale par IP (complément DRF throttling)."""
import time

from django.http import JsonResponse

_CACHE = {}
_WINDOW = 60
_MAX = int(__import__('os').environ.get('MIDDLEWARE_RATE_PER_MIN', '300'))


class GlobalRateLimitMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.path.startswith('/api/'):
            ip = request.META.get('REMOTE_ADDR', 'unknown')
            now = time.time()
            bucket = _CACHE.setdefault(ip, [])
            bucket[:] = [t for t in bucket if now - t < _WINDOW]
            if len(bucket) >= _MAX:
                return JsonResponse(
                    {'detail': 'Trop de requêtes. Réessayez dans une minute.'},
                    status=429,
                )
            bucket.append(now)
        return self.get_response(request)
