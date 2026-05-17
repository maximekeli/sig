from django.contrib import admin
from django.contrib.gis.admin import GISModelAdmin

from .models import AdministrativeZone, SoilPoint, SoilPointNasaSnapshot


@admin.register(AdministrativeZone)
class AdministrativeZoneAdmin(GISModelAdmin):
    list_display = ('name', 'code', 'zone_type')
    list_filter = ('zone_type',)


@admin.register(SoilPoint)
class SoilPointAdmin(GISModelAdmin):
    list_display = ('id', 'ph', 'soil_type', 'humidity_pct', 'collected_at', 'is_validated')
    list_filter = ('soil_type', 'fertility_class', 'is_validated')


@admin.register(SoilPointNasaSnapshot)
class SoilPointNasaSnapshotAdmin(admin.ModelAdmin):
    list_display = ('soil_point', 'product', 'value', 'observed_at')
