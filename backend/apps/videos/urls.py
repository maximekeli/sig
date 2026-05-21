from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import VideoCommentViewSet, VideoPostViewSet

router = DefaultRouter()
router.register('posts', VideoPostViewSet, basename='video-post')
router.register('comments', VideoCommentViewSet, basename='video-comment')

urlpatterns = [
    path('', include(router.urls)),
]
