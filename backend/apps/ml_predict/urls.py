from django.urls import path

from .views import ModelMetricsView, PredictFertilityView, TrainModelView

urlpatterns = [
    path('predict/', PredictFertilityView.as_view(), name='ml-predict'),
    path('train/', TrainModelView.as_view(), name='ml-train'),
    path('metrics/', ModelMetricsView.as_view(), name='ml-metrics'),
]
