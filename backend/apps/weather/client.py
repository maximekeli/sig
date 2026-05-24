"""Client OpenWeatherMap — météo actuelle et prévisions."""
from __future__ import annotations

import logging
from typing import Any

import requests
from django.conf import settings
from django.core.cache import cache

logger = logging.getLogger(__name__)

OPENWEATHER_BASE = 'https://api.openweathermap.org/data/2.5'


class OpenWeatherError(Exception):
    """Erreur d'appel OpenWeather."""


def is_configured() -> bool:
    return bool(getattr(settings, 'OPENWEATHER_API_KEY', ''))


def _api_key() -> str:
    key = getattr(settings, 'OPENWEATHER_API_KEY', '')
    if not key:
        raise OpenWeatherError(
            'OpenWeather non configuré : définissez OPENWEATHER_API_KEY dans .env',
        )
    return key


def _cache_key(kind: str, lat: float, lon: float) -> str:
    return f'openweather:{kind}:{round(lat, 2)}:{round(lon, 2)}'


def _in_maritime_region(lat: float, lon: float) -> bool:
    min_lon, min_lat, max_lon, max_lat = settings.REGION_MARITIME_BBOX
    return min_lon <= lon <= max_lon and min_lat <= lat <= max_lat


def _normalize_current(data: dict) -> dict:
    main = data.get('main') or {}
    wind = data.get('wind') or {}
    weather_list = data.get('weather') or [{}]
    w0 = weather_list[0] if weather_list else {}
    rain = data.get('rain') or {}
    return {
        'temp_c': main.get('temp'),
        'feels_like_c': main.get('feels_like'),
        'humidity_pct': main.get('humidity'),
        'pressure_hpa': main.get('pressure'),
        'wind_speed_ms': wind.get('speed'),
        'wind_deg': wind.get('deg'),
        'description': w0.get('description', ''),
        'icon': w0.get('icon', ''),
        'clouds_pct': (data.get('clouds') or {}).get('all'),
        'rain_1h_mm': rain.get('1h') or rain.get('3h'),
        'visibility_m': data.get('visibility'),
        'location': data.get('name', ''),
        'sunrise': data.get('sys', {}).get('sunrise'),
        'sunset': data.get('sys', {}).get('sunset'),
        'raw_dt': data.get('dt'),
    }


def _normalize_forecast(data: dict, max_items: int = 8) -> list[dict]:
    items = []
    for entry in (data.get('list') or [])[:max_items]:
        main = entry.get('main') or {}
        weather_list = entry.get('weather') or [{}]
        w0 = weather_list[0] if weather_list else {}
        items.append({
            'dt': entry.get('dt'),
            'temp_c': main.get('temp'),
            'humidity_pct': main.get('humidity'),
            'description': w0.get('description', ''),
            'icon': w0.get('icon', ''),
            'pop': entry.get('pop'),
            'rain_3h_mm': (entry.get('rain') or {}).get('3h'),
        })
    return items


def fetch_current(lat: float, lon: float, *, force_refresh: bool = False) -> dict[str, Any]:
    if not _in_maritime_region(lat, lon):
        raise OpenWeatherError('Coordonnées hors zone pilote Maritime Togo.')

    key = _cache_key('current', lat, lon)
    if not force_refresh:
        cached = cache.get(key)
        if cached:
            return cached

    url = f'{OPENWEATHER_BASE}/weather'
    params = {
        'lat': lat,
        'lon': lon,
        'appid': _api_key(),
        'units': 'metric',
        'lang': 'fr',
    }
    try:
        resp = requests.get(url, params=params, timeout=20)
        if not resp.ok:
            raise OpenWeatherError(f'OpenWeather HTTP {resp.status_code}: {(resp.text or "")[:300]}')
        payload = resp.json()
    except requests.RequestException as exc:
        logger.warning('OpenWeather current failed: %s', exc)
        raise OpenWeatherError(f'Météo actuelle indisponible : {exc}') from exc

    result = {
        'lat': lat,
        'lon': lon,
        'current': _normalize_current(payload),
        'provider': 'OpenWeatherMap',
    }
    cache.set(key, result, timeout=getattr(settings, 'OPENWEATHER_CACHE_SECONDS', 600))
    return result


def fetch_forecast(lat: float, lon: float, *, force_refresh: bool = False) -> dict[str, Any]:
    if not _in_maritime_region(lat, lon):
        raise OpenWeatherError('Coordonnées hors zone pilote Maritime Togo.')

    key = _cache_key('forecast', lat, lon)
    if not force_refresh:
        cached = cache.get(key)
        if cached:
            return cached

    url = f'{OPENWEATHER_BASE}/forecast'
    params = {
        'lat': lat,
        'lon': lon,
        'appid': _api_key(),
        'units': 'metric',
        'lang': 'fr',
        'cnt': 8,
    }
    try:
        resp = requests.get(url, params=params, timeout=25)
        if not resp.ok:
            raise OpenWeatherError(f'OpenWeather HTTP {resp.status_code}: {(resp.text or "")[:300]}')
        payload = resp.json()
    except requests.RequestException as exc:
        logger.warning('OpenWeather forecast failed: %s', exc)
        raise OpenWeatherError(f'Prévisions indisponibles : {exc}') from exc

    city = payload.get('city') or {}
    result = {
        'lat': lat,
        'lon': lon,
        'city': city.get('name', ''),
        'forecast': _normalize_forecast(payload),
        'provider': 'OpenWeatherMap',
    }
    cache.set(key, result, timeout=getattr(settings, 'OPENWEATHER_CACHE_SECONDS', 600))
    return result


def weather_summary_for_point(lat: float, lon: float) -> dict[str, Any]:
    """Résumé météo pour parcelles / recommandations agricoles."""
    if not is_configured():
        return {'configured': False}
    try:
        current = fetch_current(lat, lon)
        cur = current['current']
        tips = []
        temp = cur.get('temp_c')
        humidity = cur.get('humidity_pct')
        rain = cur.get('rain_1h_mm')
        if temp is not None and temp > 35:
            tips.append('Forte chaleur : privilégier arrosage tôt le matin.')
        if humidity is not None and humidity < 40:
            tips.append('Air sec : surveiller le stress hydrique des cultures.')
        if rain and float(rain) > 0:
            tips.append('Pluie récente : adapter les travaux au sol.')
        return {
            'configured': True,
            **current,
            'agro_tips': tips[:4],
        }
    except OpenWeatherError as exc:
        return {'configured': True, 'error': str(exc)}
