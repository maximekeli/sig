from django.contrib import admin

from .models import NasaLayerCatalog


@admin.register(NasaLayerCatalog)
class NasaLayerCatalogAdmin(admin.ModelAdmin):
    list_display = ('product', 'layer_name', 'acquisition_date', 'is_active')
    list_filter = ('product', 'is_active')
