from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    NasaCatalogSummaryView,
    NasaEnrichPointsView,
    NasaIngestTriggerView,
    NasaLayerViewSet,
    NasaTilePlaceholderView,
)

router = DefaultRouter()
router.register('layers', NasaLayerViewSet, basename='nasa-layers')

urlpatterns = [
    path('', include(router.urls)),
    path('catalog/summary/', NasaCatalogSummaryView.as_view(), name='nasa-summary'),
    path('ingest/', NasaIngestTriggerView.as_view(), name='nasa-ingest'),
    path('enrich-points/', NasaEnrichPointsView.as_view(), name='nasa-enrich-points'),
    path(
        'tiles/<str:product>/<str:date_str>/<int:z>/<int:x>/<int:y>.png',
        NasaTilePlaceholderView.as_view(),
        name='nasa-tile',
    ),
]
