from django.contrib.gis.db import models


class NasaLayerCatalog(models.Model):
    """Inventory of integrated NASA products (≥50 images target)."""

    class Product(models.TextChoices):
        MOD13Q1 = 'MOD13Q1', 'MODIS NDVI/EVI'
        SMAP = 'SMAP', 'SMAP Soil Moisture'
        GPM = 'GPM', 'GPM Precipitation'
        SRTM = 'SRTM', 'SRTM Elevation'
        MOD16 = 'MOD16', 'MOD16 Evapotranspiration'
        MOD11A2 = 'MOD11A2', 'MODIS Land Surface Temp'
        ECOSTRESS = 'ECOSTRESS', 'ECOSTRESS ET'

    product = models.CharField(max_length=20, choices=Product.choices)
    layer_name = models.CharField(max_length=200)
    acquisition_date = models.DateField()
    bbox = models.PolygonField(srid=4326, null=True, blank=True)
    raster_path = models.CharField(max_length=500, blank=True)
    tile_url_template = models.CharField(
        max_length=500, blank=True,
        help_text='WMS/XYZ template for Leaflet overlay',
    )
    metadata = models.JSONField(default=dict, blank=True)
    is_active = models.BooleanField(default=True)
    ingested_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Couche NASA'
        verbose_name_plural = 'Catalogue NASA'
        ordering = ['-acquisition_date']
        indexes = [models.Index(fields=['product', 'acquisition_date'])]

    def __str__(self):
        return f'{self.product} — {self.acquisition_date}'
