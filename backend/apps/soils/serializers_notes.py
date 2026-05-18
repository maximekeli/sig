from rest_framework import serializers

from .models import SoilPointNote


class SoilPointNoteSerializer(serializers.ModelSerializer):
    author_name = serializers.CharField(source='author.username', read_only=True)

    class Meta:
        model = SoilPointNote
        fields = ('id', 'soil_point', 'author', 'author_name', 'text', 'created_at')
        read_only_fields = ('author', 'created_at')
