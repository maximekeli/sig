from django.conf import settings
from django.contrib.gis.db import models
from django.core.validators import MaxValueValidator, MinValueValidator


class AdministrativeZone(models.Model):
    """Cantons, préfectures — polygon zones (≥10 per ToR)."""

    class ZoneType(models.TextChoices):
        REGION = 'region', 'Région'
        PREFECTURE = 'prefecture', 'Préfecture'
        CANTON = 'canton', 'Canton'
        DEGRADED = 'degraded', 'Zone dégradée'

    name = models.CharField(max_length=200)
    code = models.CharField(max_length=50, unique=True)
    zone_type = models.CharField(max_length=20, choices=ZoneType.choices)
    geometry = models.MultiPolygonField(srid=4326)
    parent = models.ForeignKey(
        'self', null=True, blank=True, on_delete=models.SET_NULL, related_name='children',
    )
    metadata = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Zone administrative'
        verbose_name_plural = 'Zones administratives'
        indexes = [models.Index(fields=['zone_type', 'code'])]

    def __str__(self):
        return f'{self.name} ({self.code})'


class SoilPoint(models.Model):
    """Historical and field soil sample points (≥150 target)."""

    class SoilType(models.TextChoices):
        CLAY = 'argileux', 'Argileux'
        SANDY = 'sableux', 'Sableux'
        LOAM = 'limoneux', 'Limoneux'
        PEAT = 'tourbeux', 'Tourbeux'
        LIME = 'calcaire', 'Calcaire'

    class FertilityClass(models.TextChoices):
        LOW = 'faible', 'Faible'
        MEDIUM = 'moyenne', 'Moyenne'
        HIGH = 'elevee', 'Élevée'

    location = models.PointField(srid=4326)
    ph = models.FloatField(
        validators=[MinValueValidator(3.5), MaxValueValidator(9.5)],
        help_text='pH mesuré terrain',
    )
    humidity_pct = models.FloatField(
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        help_text='Humidité %',
    )
    soil_type = models.CharField(max_length=20, choices=SoilType.choices)
    fertility_class = models.CharField(
        max_length=20, choices=FertilityClass.choices, blank=True,
    )
    fertility_score = models.FloatField(
        null=True, blank=True,
        validators=[MinValueValidator(0), MaxValueValidator(1)],
    )
    photo = models.ImageField(upload_to='soil_photos/%Y/%m/', blank=True)
    slope_pct = models.FloatField(null=True, blank=True)
    ndvi_3m_avg = models.FloatField(null=True, blank=True)
    smap_moisture_avg = models.FloatField(null=True, blank=True)
    elevation_m = models.FloatField(null=True, blank=True)
    notes = models.TextField(blank=True)
    source = models.CharField(max_length=100, default='terrain')
    producer = models.CharField(max_length=100, blank=True)
    collected_at = models.DateField()
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True, blank=True,
        on_delete=models.SET_NULL,
        related_name='soil_points',
    )
    zone = models.ForeignKey(
        AdministrativeZone, null=True, blank=True,
        on_delete=models.SET_NULL, related_name='soil_points',
    )
    is_validated = models.BooleanField(default=False)
    quality_flags = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Point de sol'
        verbose_name_plural = 'Points de sol'
        indexes = [
            models.Index(fields=['ph', 'soil_type']),
            models.Index(fields=['collected_at']),
        ]

    def __str__(self):
        return f'Sol #{self.pk} pH={self.ph}'

    @property
    def ph_color(self):
        """ToR color coding: RED <5.5, YELLOW 5.5-7, GREEN >7."""
        if self.ph < 5.5:
            return 'red'
        if self.ph <= 7.0:
            return 'yellow'
        return 'green'


class SoilPointNasaSnapshot(models.Model):
    """Time series / snapshot of NASA values at a soil point."""

    soil_point = models.ForeignKey(SoilPoint, on_delete=models.CASCADE, related_name='nasa_snapshots')
    product = models.CharField(max_length=50)  # MOD13Q1, SMAP, etc.
    value = models.FloatField()
    observed_at = models.DateField()
    metadata = models.JSONField(default=dict, blank=True)

    class Meta:
        unique_together = ('soil_point', 'product', 'observed_at')
        ordering = ['-observed_at']
