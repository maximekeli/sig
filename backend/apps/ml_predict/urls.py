from django.urls import path

from .views import (
    BatchPredictExportView,
    BatchPredictView,
    ModelMetricsView,
    PredictFertilityView,
    TrainModelView,
)

urlpatterns = [
    path('predict/', PredictFertilityView.as_view(), name='ml-predict'),
    path('predict/batch/', BatchPredictView.as_view(), name='ml-predict-batch'),
    path('predict/batch/export/', BatchPredictExportView.as_view(), name='ml-predict-export'),
    path('train/', TrainModelView.as_view(), name='ml-train'),
    path('metrics/', ModelMetricsView.as_view(), name='ml-metrics'),
]
