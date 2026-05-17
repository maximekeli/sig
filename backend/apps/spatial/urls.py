from django.urls import path

from .views import (
    AreaView,
    BufferView,
    IntersectionView,
    NdviTimeseriesView,
    ProximityView,
    SmapCorrelationView,
    SpatialStatisticsView,
    VulnerabilityZoningView,
)

urlpatterns = [
    path('proximity/', ProximityView.as_view(), name='spatial-proximity'),
    path('intersection/', IntersectionView.as_view(), name='spatial-intersection'),
    path('buffer/', BufferView.as_view(), name='spatial-buffer'),
    path('area/', AreaView.as_view(), name='spatial-area'),
    path('vulnerability/', VulnerabilityZoningView.as_view(), name='spatial-vulnerability'),
    path('ndvi-timeseries/<int:point_id>/', NdviTimeseriesView.as_view(), name='spatial-ndvi-ts'),
    path('statistics/', SpatialStatisticsView.as_view(), name='spatial-statistics'),
    path('smap-correlation/', SmapCorrelationView.as_view(), name='spatial-smap-corr'),
]
