"""
NASA data ingestion — earthaccess + pystac-client + rasterio/xarray.
Weekly automated via Celery; credentials via NASA_EARTHDATA_* env vars.
"""
import logging
from datetime import date, timedelta
from pathlib import Path

from django.conf import settings
from django.contrib.gis.geos import Polygon

from .earthdata import EARTHDATA_PRODUCTS, search_and_download
from .models import NasaLayerCatalog
from .stac_client import search_granules

logger = logging.getLogger(__name__)

PRODUCTS = [
    ('MOD13Q1', 'MODIS NDVI/EVI', 16),
    ('SMAP', 'SMAP L3 Soil Moisture', 3),
    ('GPM', 'GPM IMERG Precipitation', 1),
    ('SRTM', 'SRTM DEM 30m', 365),
    ('MOD16', 'MOD16 Evapotranspiration', 8),
]


def _maritime_bbox() -> tuple[float, float, float, float]:
    return settings.REGION_MARITIME_BBOX


def _maritime_bbox_polygon():
    return Polygon.from_bbox(_maritime_bbox())


def ingest_product(product_code: str, layer_label: str, days_back: int = 30) -> int:
    """
    Register catalog entries + optional Earthdata download + STAC metadata.
    """
    cache_dir = Path(settings.NASA_CACHE_DIR)
    cache_dir.mkdir(parents=True, exist_ok=True)
    bbox = _maritime_bbox()
    bbox_poly = _maritime_bbox_polygon()
    created = 0
    today = date.today()
    start = today - timedelta(days=days_back)

    # STAC discovery (no auth required for search metadata)
    stac_items = search_granules(product_code, start, today, bbox, limit=5)

    for i in range(min(days_back, 30)):
        acq = today - timedelta(days=i * max(1, days_back // 10))
        layer_name = f'{product_code}_{acq.isoformat()}_maritime'
        if NasaLayerCatalog.objects.filter(product=product_code, acquisition_date=acq).exists():
            continue

        raster_path = str(cache_dir / f'{layer_name}.tif')
        downloaded = _download_via_earthaccess(product_code, acq, bbox)

        meta = {
            'source': 'NASA Earthdata',
            'crs': 'EPSG:4326',
            'credit': 'NASA Earth Science',
            'demo_mode': not bool(
                settings.NASA_EARTHDATA_USERNAME or getattr(settings, 'NASA_EARTHDATA_TOKEN', ''),
            ),
            'stac_items_found': len(stac_items),
        }
        if stac_items:
            meta['stac_sample'] = stac_items[0]
        if downloaded:
            meta['downloaded_files'] = downloaded
            meta['demo_mode'] = False
            from .raster_utils import clip_raster_to_bbox
            for fpath in downloaded:
                clipped = clip_raster_to_bbox(fpath, raster_path, bbox)
                if clipped:
                    raster_path = clipped
                    break

        NasaLayerCatalog.objects.create(
            product=product_code,
            layer_name=layer_name,
            acquisition_date=acq,
            bbox=bbox_poly,
            raster_path=raster_path,
            tile_url_template=_demo_tile_url(product_code, acq),
            metadata=meta,
        )
        created += 1

    return created


def _download_via_earthaccess(product_code: str, acq: date, bbox: tuple) -> list[str]:
    spec = EARTHDATA_PRODUCTS.get(product_code)
    if not spec:
        return []
    short_name, version = spec
    temporal = (acq.isoformat(), (acq + timedelta(days=1)).isoformat())
    return search_and_download(
        short_name=short_name,
        version=version,
        bounding_box=bbox,
        temporal=temporal,
        count=1,
    )


def _demo_tile_url(product: str, acq: date) -> str:
    return f'/api/v1/nasa/tiles/{product}/{acq.isoformat()}/{{z}}/{{x}}/{{y}}.png'


def enrich_soil_points_from_rasters(limit: int = 100) -> int:
    """
    Extract NDVI / SMAP from cached rasters onto SoilPoint records.
    Uses rasterio point sampling.
    """
    from soils.models import SoilPoint

    from .raster_utils import extract_point_value, ndvi_from_mod13

    updated = 0
    modis_layers = NasaLayerCatalog.objects.filter(
        product='MOD13Q1', raster_path__isnull=False,
    ).exclude(raster_path='').order_by('-acquisition_date')[:3]
    smap_layers = NasaLayerCatalog.objects.filter(
        product='SMAP',
    ).exclude(raster_path='').order_by('-acquisition_date')[:3]

    modis_path = next((p.raster_path for p in modis_layers if Path(p.raster_path).exists()), None)
    smap_path = next((p.raster_path for p in smap_layers if Path(p.raster_path).exists()), None)

    for point in SoilPoint.objects.filter(is_validated=True)[:limit]:
        lon, lat = point.location.x, point.location.y
        changed = False
        if modis_path and point.ndvi_3m_avg is None:
            ndvi = ndvi_from_mod13(modis_path, lon, lat)
            if ndvi is not None:
                point.ndvi_3m_avg = round(ndvi, 4)
                changed = True
        if smap_path and point.smap_moisture_avg is None:
            smap = extract_point_value(smap_path, lon, lat)
            if smap is not None:
                point.smap_moisture_avg = round(float(smap), 4)
                changed = True
        if changed:
            point.save(update_fields=['ndvi_3m_avg', 'smap_moisture_avg'])
            updated += 1
    return updated


def ingest_all() -> dict:
    totals = {}
    for code, label, _freq in PRODUCTS:
        totals[code] = ingest_product(code, label, days_back=90)
    totals['soil_points_enriched'] = enrich_soil_points_from_rasters()
    return totals
