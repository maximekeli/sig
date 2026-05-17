"""
Raster processing — rasterio + xarray + rioxarray.
Clip to bbox, extract point values, reproject to EPSG:4326.
"""
import logging
from pathlib import Path
from typing import Optional

import numpy as np

logger = logging.getLogger(__name__)


def clip_raster_to_bbox(
    input_path: str | Path,
    output_path: str | Path,
    bbox: tuple[float, float, float, float],
) -> Optional[str]:
    """Clip GeoTIFF/NetCDF to WGS84 bbox and save as GeoTIFF."""
    min_lon, min_lat, max_lon, max_lat = bbox
    input_path = Path(input_path)
    output_path = Path(output_path)
    if not input_path.exists():
        return None

    try:
        import rioxarray
        import xarray as xr

        da = xr.open_dataarray(input_path, engine='rasterio', mask_and_scale=True)
        if da.rio.crs is None:
            da = da.rio.write_crs('EPSG:4326')
        da = da.rio.clip_box(
            minx=min_lon, miny=min_lat, maxx=max_lon, maxy=max_lat,
        )
        if da.rio.crs and str(da.rio.crs) != 'EPSG:4326':
            da = da.rio.reproject('EPSG:4326')
        da.rio.to_raster(output_path, driver='GTiff')
        return str(output_path)
    except Exception:
        pass

    try:
        import rasterio
        from rasterio.mask import mask
        from shapely.geometry import box

        geom = [box(min_lon, min_lat, max_lon, max_lat).__geo_interface__]
        with rasterio.open(input_path) as src:
            out_image, out_transform = mask(src, geom, crop=True)
            out_meta = src.meta.copy()
            out_meta.update({
                'driver': 'GTiff',
                'height': out_image.shape[1],
                'width': out_image.shape[2],
                'transform': out_transform,
                'crs': 'EPSG:4326',
            })
            with rasterio.open(output_path, 'w', **out_meta) as dst:
                dst.write(out_image)
        return str(output_path)
    except Exception as exc:
        logger.warning('clip_raster failed: %s', exc)
        return None


def extract_point_value(
    raster_path: str | Path,
    lon: float,
    lat: float,
    band: int = 1,
) -> Optional[float]:
    """Sample raster at lon/lat (nearest pixel)."""
    raster_path = Path(raster_path)
    if not raster_path.exists():
        return None
    try:
        import rasterio
        with rasterio.open(raster_path) as src:
            row, col = src.index(lon, lat)
            val = src.read(band, window=((row, row + 1), (col, col + 1)))
            v = float(val[0, 0])
            if src.nodata is not None and v == src.nodata:
                return None
            if np.isnan(v):
                return None
            return v
    except Exception as exc:
        logger.debug('extract_point_value: %s', exc)
        return None


def ndvi_from_mod13(path: str | Path, lon: float, lat: float) -> Optional[float]:
    """MOD13Q1: band 1 often NDVI (scale 0.0001)."""
    raw = extract_point_value(path, lon, lat, band=1)
    if raw is None:
        return None
    if abs(raw) > 2:
        return raw * 0.0001
    return raw
