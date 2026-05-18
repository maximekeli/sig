from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .extra_views import (
    HeatmapDataView,
    PendingValidationView,
    SoilPointCompareView,
    SoilPointNoteViewSet,
)
from .views import AdministrativeZoneViewSet, DashboardStatsView, SoilPointViewSet

router = DefaultRouter()
router.register('points', SoilPointViewSet, basename='soil-points')
router.register('zones', AdministrativeZoneViewSet, basename='admin-zones')
router.register('notes', SoilPointNoteViewSet, basename='soil-notes')

urlpatterns = [
    path('', include(router.urls)),
    path('dashboard/stats/', DashboardStatsView.as_view(), name='dashboard-stats'),
    path('heatmap/', HeatmapDataView.as_view(), name='soil-heatmap'),
    path('points/<int:pk>/compare/', SoilPointCompareView.as_view(), name='soil-compare'),
    path('validation/pending/', PendingValidationView.as_view(), name='soil-pending'),
]
