from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .extended_views import StoryViewSet
from .views import VideoCommentViewSet, VideoPostViewSet

router = DefaultRouter()
router.register('posts', VideoPostViewSet, basename='video-post')
router.register('comments', VideoCommentViewSet, basename='video-comment')
router.register('stories', StoryViewSet, basename='video-story')

urlpatterns = [
    path('', include(router.urls)),
]
