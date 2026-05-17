from django.contrib import admin

from .models import FertilityModelRun, FertilityPredictionLog


@admin.register(FertilityModelRun)
class FertilityModelRunAdmin(admin.ModelAdmin):
    list_display = ('id', 'algorithm', 'f1_macro', 'sample_count', 'is_active', 'trained_at')


@admin.register(FertilityPredictionLog)
class FertilityPredictionLogAdmin(admin.ModelAdmin):
    list_display = ('id', 'predicted_class', 'inference_ms', 'created_at')
