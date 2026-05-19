from django.urls import path

from .views import (
    AreaView,
    BufferView,
    IntersectionView,
    NdviTimeseriesView,
    ParcelAnalyzeView,
    ParcelLiveView,
    ParcelZonesGeoJsonView,
    ParcelZonesListView,
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
    path('parcel/analyze/', ParcelAnalyzeView.as_view(), name='spatial-parcel-analyze'),
    path('parcel/live/', ParcelLiveView.as_view(), name='spatial-parcel-live'),
    path('parcel/zones/geojson/', ParcelZonesGeoJsonView.as_view(), name='spatial-parcel-zones-geojson'),
    path('parcel/zones/', ParcelZonesListView.as_view(), name='spatial-parcel-zones'),
]
