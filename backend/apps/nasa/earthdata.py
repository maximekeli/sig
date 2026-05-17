"""
NASA Earthdata download via earthaccess.
Set NASA_EARTHDATA_USERNAME + NASA_EARTHDATA_PASSWORD in .env
"""
import logging
import os
from pathlib import Path

from django.conf import settings

logger = logging.getLogger(__name__)


def login() -> bool:
    """Authenticate with NASA Earthdata (environment or .netrc)."""
    if not settings.NASA_EARTHDATA_USERNAME:
        return False
    os.environ.setdefault('EARTHDATA_USERNAME', settings.NASA_EARTHDATA_USERNAME)
    os.environ.setdefault('EARTHDATA_PASSWORD', settings.NASA_EARTHDATA_PASSWORD)
    try:
        import earthaccess
        auth = earthaccess.login(strategy='environment')
        return auth is not None
    except Exception as exc:
        logger.warning('earthaccess login failed: %s', exc)
        return False


def search_and_download(
    short_name: str,
    version: str,
    bounding_box: tuple[float, float, float, float],
    temporal: tuple[str, str],
    count: int = 2,
    output_dir: Path | None = None,
) -> list[str]:
    """
    Search granules by short name and download to cache.
    Returns list of local file paths.
    """
    if not login():
        return []

    output_dir = output_dir or Path(settings.NASA_CACHE_DIR)
    output_dir.mkdir(parents=True, exist_ok=True)

    try:
        import earthaccess
        results = earthaccess.search_data(
            short_name=short_name,
            version=version,
            bounding_box=bounding_box,
            temporal=temporal,
            count=count,
        )
        if not results:
            return []
        files = earthaccess.download(results, local_path=str(output_dir))
        return [str(f) for f in files] if files else []
    except Exception as exc:
        logger.warning('earthaccess download %s: %s', short_name, exc)
        return []


# Product → Earthdata short_name / version (OS2 mapping)
EARTHDATA_PRODUCTS = {
    'MOD13Q1': ('MOD13Q1', '061'),
    'SMAP': ('SPL3SMP_E', '006'),
    'GPM': ('GPM_3IMERGDF', '07'),
    'MOD16': ('MOD16A2GF', '061'),
}
