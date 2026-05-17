"""
STAC catalog search via pystac-client — MODIS, SMAP, GPM, etc.
https://github.com/stac-utils/pystac-client
"""
import logging
from datetime import date, timedelta
from typing import Any

from django.conf import settings

logger = logging.getLogger(__name__)

# NASA CMR-STAC / LPCLOUD / GES DISC endpoints (public catalogs)
STAC_CATALOGS = {
    'MOD13Q1': 'https://cmr.earthdata.nasa.gov/stac/LPCLOUD',
    'SMAP': 'https://cmr.earthdata.nasa.gov/stac/NSIDC',
    'GPM': 'https://cmr.earthdata.nasa.gov/stac/GES_DISC',
    'SRTM': 'https://cmr.earthdata.nasa.gov/stac/LPCLOUD',
    'MOD16': 'https://cmr.earthdata.nasa.gov/stac/LPCLOUD',
}

# Collection IDs (may vary; search falls back to text query)
COLLECTION_HINTS = {
    'MOD13Q1': 'MOD13Q1',
    'SMAP': 'SPL3SMP',
    'GPM': 'IMERG',
    'SRTM': 'SRTM',
    'MOD16': 'MOD16A2',
}


def search_granules(
    product_code: str,
    start: date,
    end: date,
    bbox: tuple[float, float, float, float],
    limit: int = 10,
) -> list[dict[str, Any]]:
    """
    Search STAC items for Maritime Togo bbox.
    Returns list of metadata dicts (id, datetime, assets, href).
    """
    catalog_url = STAC_CATALOGS.get(product_code)
    if not catalog_url:
        return []

    try:
        from pystac_client import Client
    except ImportError:
        logger.warning('pystac-client not installed')
        return []

    try:
        client = Client.open(catalog_url)
        min_lon, min_lat, max_lon, max_lat = bbox
        search = client.search(
            collections=[COLLECTION_HINTS.get(product_code)] if COLLECTION_HINTS.get(product_code) else None,
            bbox=[min_lon, min_lat, max_lon, max_lat],
            datetime=f'{start.isoformat()}/{end.isoformat()}',
            max_items=limit,
        )
        results = []
        for item in search.items():
            results.append({
                'id': item.id,
                'datetime': item.datetime.isoformat() if item.datetime else None,
                'assets': list(item.assets.keys()),
                'bbox': item.bbox,
                'self_href': item.self_href,
            })
        return results
    except Exception as exc:
        logger.info('STAC search %s: %s (catalog may need auth)', product_code, exc)
        return []
