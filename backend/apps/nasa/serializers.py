from rest_framework import serializers

from .models import NasaLayerCatalog


class NasaLayerSerializer(serializers.ModelSerializer):
    class Meta:
        model = NasaLayerCatalog
        fields = (
            'id', 'product', 'layer_name', 'acquisition_date',
            'tile_url_template', 'metadata', 'is_active', 'ingested_at',
        )
