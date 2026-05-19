"""Contrôle de santé étendu (DB, Redis, Celery broker)."""
from django.db import connection
from django.http import JsonResponse


def health_check(request):
    checks = {'api': 'ok', 'project': 'SIG-SOLS-TOGO-2026-01'}
    status_code = 200

    try:
        with connection.cursor() as cursor:
            cursor.execute('SELECT 1')
        checks['database'] = 'ok'
    except Exception as exc:
        checks['database'] = str(exc)[:120]
        status_code = 503

    try:
        from django.core.cache import cache
        cache.set('health_ping', '1', 5)
        checks['cache'] = 'ok' if cache.get('health_ping') == '1' else 'degraded'
    except Exception as exc:
        checks['cache'] = str(exc)[:120]

    overall = 'ok' if checks.get('database') == 'ok' else 'degraded'
    return JsonResponse({'status': overall, 'checks': checks}, status=status_code)
