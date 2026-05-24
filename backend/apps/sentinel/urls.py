from django.urls import path

from .views import (
    SentinelAnalyzeView,
    SentinelLayersView,
    SentinelPreviewView,
    SentinelStatusView,
    SentinelTileView,
)

urlpatterns = [
    path('status/', SentinelStatusView.as_view(), name='sentinel-status'),
    path('layers/', SentinelLayersView.as_view(), name='sentinel-layers'),
    path('analyze/', SentinelAnalyzeView.as_view(), name='sentinel-analyze'),
    path('preview/', SentinelPreviewView.as_view(), name='sentinel-preview'),
    path(
        'tiles/<str:layer>/<int:z>/<int:x>/<int:y>.png',
        SentinelTileView.as_view(),
        name='sentinel-tile',
    ),
]
