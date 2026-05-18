from django.db import models


class FertilityModelRun(models.Model):
    """Training run metadata and metrics."""

    algorithm = models.CharField(max_length=50, default='RandomForest')
    sample_count = models.IntegerField()
    f1_macro = models.FloatField(null=True, blank=True)
    auc_roc = models.FloatField(null=True, blank=True)
    feature_importance = models.JSONField(default=dict, blank=True)
    confusion_matrix = models.JSONField(default=dict, blank=True)
    model_path = models.CharField(max_length=500)
    is_active = models.BooleanField(default=True)
    trained_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-trained_at']


class FertilityPredictionLog(models.Model):
    soil_point = models.ForeignKey(
        'soils.SoilPoint', null=True, blank=True, on_delete=models.SET_NULL,
    )
    input_features = models.JSONField()
    predicted_class = models.CharField(max_length=20)
    predicted_score = models.FloatField()
    recommendation = models.TextField()
    inference_ms = models.FloatField()
    created_at = models.DateTimeField(auto_now_add=True)
