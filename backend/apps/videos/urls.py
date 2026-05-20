from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import VideoPostViewSet

router = DefaultRouter()
router.register('posts', VideoPostViewSet, basename='video-post')

urlpatterns = [
    path('', include(router.urls)),
]
