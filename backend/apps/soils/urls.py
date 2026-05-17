from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import AdministrativeZoneViewSet, DashboardStatsView, SoilPointViewSet

router = DefaultRouter()
router.register('points', SoilPointViewSet, basename='soil-points')
router.register('zones', AdministrativeZoneViewSet, basename='admin-zones')

urlpatterns = [
    path('', include(router.urls)),
    path('dashboard/stats/', DashboardStatsView.as_view(), name='dashboard-stats'),
]
