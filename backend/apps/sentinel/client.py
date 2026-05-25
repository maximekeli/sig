"""Client Sentinel Hub — OAuth + Process API."""
from __future__ import annotations

import logging
import math
from datetime import date, timedelta

import requests
from django.conf import settings
from django.core.cache import cache

from .evalscripts import LAYER_PRESETS, NDVI_STATS

logger = logging.getLogger(__name__)

TOKEN_CACHE_KEY = 'sentinel_hub:oauth_token'


class SentinelHubError(Exception):
    """Erreur d’appel Sentinel Hub."""


def is_configured() -> bool:
    secret = settings.SENTINEL_HUB_CLIENT_SECRET
    return bool(settings.SENTINEL_HUB_CLIENT_ID and secret)


def has_secret() -> bool:
    return bool(settings.SENTINEL_HUB_CLIENT_SECRET)


def _base_url() -> str:
    return settings.SENTINEL_HUB_BASE_URL.rstrip('/')


def get_access_token(*, force_refresh: bool = False) -> str:
    if not is_configured():
        raise SentinelHubError(
            'Sentinel Hub non configuré : définissez SENTINEL_HUB_CLIENT_ID et '
            'SENTINEL_HUB_CLIENT_SECRET (ou SENTINEL_HUB_API_KEY) dans .env',
        )
    if not force_refresh:
        cached = cache.get(TOKEN_CACHE_KEY)
        if cached:
            return cached

    url = settings.SENTINEL_HUB_TOKEN_URL
    try:
        resp = requests.post(
            url,
            data={
                'grant_type': 'client_credentials',
                'client_id': settings.SENTINEL_HUB_CLIENT_ID,
                'client_secret': settings.SENTINEL_HUB_CLIENT_SECRET,
            },
            headers={'content-type': 'application/x-www-form-urlencoded'},
            timeout=30,
        )
        if not resp.ok:
            detail = (resp.text or '')[:400]
            raise SentinelHubError(
                f'OAuth HTTP {resp.status_code} : {detail}',
            )
        data = resp.json()
    except requests.RequestException as exc:
        logger.warning('Sentinel Hub OAuth failed: %s', exc)
        raise SentinelHubError(f'Authentification Sentinel Hub échouée : {exc}') from exc

    token = data.get('access_token')
    if not token:
        raise SentinelHubError('Réponse OAuth sans access_token.')
    ttl = max(60, int(data.get('expires_in', 3600)) - 120)
    cache.set(TOKEN_CACHE_KEY, token, timeout=ttl)
    return token


def _default_time_range(days_back: int = 30) -> tuple[str, str]:
    end = date.today()
    start = end - timedelta(days=days_back)
    return (
        f'{start.isoformat()}T00:00:00Z',
        f'{end.isoformat()}T23:59:59Z',
    )


def process_image(
    layer_id: str,
    bbox: tuple[float, float, float, float],
    *,
    width: int = 512,
    height: int = 512,
    days_back: int = 30,
    output_format: str = 'image/png',
) -> bytes:
    preset = LAYER_PRESETS.get(layer_id)
    if not preset:
        raise SentinelHubError(f'Couche inconnue : {layer_id}')

    min_lon, min_lat, max_lon, max_lat = bbox
    time_from, time_to = _default_time_range(days_back)
    payload = {
        'input': {
            'bounds': {
                'bbox': [min_lon, min_lat, max_lon, max_lat],
                'properties': {'crs': 'http://www.opengis.net/def/crs/EPSG/0/4326'},
            },
            'data': [{
                'type': 'sentinel-2-l2a',
                'dataFilter': {
                    'timeRange': {'from': time_from, 'to': time_to},
                    'maxCloudCoverage': 40,
                },
            }],
        },
        'output': {
            'width': width,
            'height': height,
            'responses': [{
                'identifier': 'default',
                'format': {'type': output_format},
            }],
        },
        'evalscript': preset['evalscript'],
    }

    token = get_access_token()
    url = f'{_base_url()}/api/v1/process'
    try:
        resp = requests.post(
            url,
            json=payload,
            headers={'Authorization': f'Bearer {token}'},
            timeout=120,
        )
        if resp.status_code == 401:
            token = get_access_token(force_refresh=True)
            resp = requests.post(
                url,
                json=payload,
                headers={'Authorization': f'Bearer {token}'},
                timeout=120,
            )
        resp.raise_for_status()
        return resp.content
    except requests.RequestException as exc:
        logger.warning('Sentinel Hub process failed: %s', exc)
        detail = ''
        if getattr(exc, 'response', None) is not None and exc.response is not None:
            detail = (exc.response.text or '')[:300]
        raise SentinelHubError(f'Process API : {exc} {detail}') from exc


def ndvi_mean_for_bbox(
    bbox: tuple[float, float, float, float],
    *,
    days_back: int = 60,
) -> dict:
    """NDVI moyen sur la bbox (échantillon raster léger)."""
    min_lon, min_lat, max_lon, max_lat = bbox
    time_from, time_to = _default_time_range(days_back)
    payload = {
        'input': {
            'bounds': {
                'bbox': [min_lon, min_lat, max_lon, max_lat],
                'properties': {'crs': 'http://www.opengis.net/def/crs/EPSG/0/4326'},
            },
            'data': [{
                'type': 'sentinel-2-l2a',
                'dataFilter': {
                    'timeRange': {'from': time_from, 'to': time_to},
                    'maxCloudCoverage': 50,
                },
            }],
        },
        'output': {
            'width': 64,
            'height': 64,
            'responses': [{
                'identifier': 'ndvi',
                'format': {'type': 'image/tiff'},
            }],
        },
        'evalscript': NDVI_STATS,
    }
    token = get_access_token()
    url = f'{_base_url()}/api/v1/process'
    try:
        resp = requests.post(
            url,
            json=payload,
            headers={'Authorization': f'Bearer {token}'},
            timeout=120,
        )
        if resp.status_code == 401:
            token = get_access_token(force_refresh=True)
            resp = requests.post(
                url,
                json=payload,
                headers={'Authorization': f'Bearer {token}'},
                timeout=120,
            )
        resp.raise_for_status()
    except requests.RequestException as exc:
        logger.warning('Sentinel Hub NDVI stats failed: %s', exc)
        detail = ''
        if getattr(exc, 'response', None) is not None and exc.response is not None:
            detail = (exc.response.text or '')[:300]
        raise SentinelHubError(f'Statistiques NDVI : {exc} {detail}') from exc
    try:
        import numpy as np
        from rasterio.io import MemoryFile
    except ImportError as exc:
        raise SentinelHubError('rasterio/numpy requis pour les statistiques NDVI.') from exc

    with MemoryFile(resp.content) as mem:
        with mem.open() as ds:
            band = ds.read(1)
    valid = band[np.isfinite(band) & (band > -1) & (band < 1)]
    if valid.size == 0:
        return {
            'ndvi_mean': None,
            'ndvi_min': None,
            'ndvi_max': None,
            'pixel_count': 0,
            'period': {'from': time_from, 'to': time_to},
        }
    return {
        'ndvi_mean': round(float(valid.mean()), 4),
        'ndvi_min': round(float(valid.min()), 4),
        'ndvi_max': round(float(valid.max()), 4),
        'pixel_count': int(valid.size),
        'period': {'from': time_from, 'to': time_to},
    }


def tile_xyz_to_bbox(z: int, x: int, y: int) -> tuple[float, float, float, float]:
    n = 2 ** z
    lon_min = x / n * 360.0 - 180.0
    lon_max = (x + 1) / n * 360.0 - 180.0
    lat_max = math.degrees(math.atan(math.sinh(math.pi * (1 - 2 * y / n))))
    lat_min = math.degrees(math.atan(math.sinh(math.pi * (1 - 2 * (y + 1) / n))))
    return lon_min, lat_min, lon_max, lat_max


def clip_bbox_to_region(
    bbox: tuple[float, float, float, float],
    region: tuple[float, float, float, float],
) -> tuple[float, float, float, float] | None:
    min_lon = max(bbox[0], region[0])
    min_lat = max(bbox[1], region[1])
    max_lon = min(bbox[2], region[2])
    max_lat = min(bbox[3], region[3])
    if min_lon >= max_lon or min_lat >= max_lat:
        return None
    return min_lon, min_lat, max_lon, max_lat
