from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView

from .messaging_views import DirectMessageListView
from .social_views import (
    FavoritesView,
    FollowUserView,
    FollowingFeedView,
    PublicProfileView,
    UserSearchView,
)
from .views import (
    ChangePasswordView,
    LiveLocationsView,
    UserTrajectoryView,
    LogoutView,
    MyLocationView,
    ProfilePhotoView,
    ProfileView,
    RegisterView,
    TokenObtainView,
    UserListView,
)

urlpatterns = [
    path('feed/', FollowingFeedView.as_view(), name='auth-feed'),
    path('favorites/', FavoritesView.as_view(), name='auth-favorites'),
    path('messages/', DirectMessageListView.as_view(), name='auth-messages'),
    path('register/', RegisterView.as_view(), name='auth-register'),
    path('token/', TokenObtainView.as_view(), name='token-obtain'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token-refresh'),
    path('logout/', LogoutView.as_view(), name='auth-logout'),
    path('profile/', ProfileView.as_view(), name='auth-profile'),
    path('profile/photo/', ProfilePhotoView.as_view(), name='auth-profile-photo'),
    path('password/change/', ChangePasswordView.as_view(), name='auth-password-change'),
    path('users/', UserListView.as_view(), name='auth-users'),
    path('users/search/', UserSearchView.as_view(), name='auth-users-search'),
    path('users/<str:username>/public/', PublicProfileView.as_view(), name='auth-user-public'),
    path('users/<str:username>/follow/', FollowUserView.as_view(), name='auth-user-follow'),
    path('location/', MyLocationView.as_view(), name='auth-location'),
    path('locations/live/', LiveLocationsView.as_view(), name='auth-locations-live'),
    path('trajectory/', UserTrajectoryView.as_view(), name='auth-trajectory-self'),
    path('trajectory/<int:user_id>/', UserTrajectoryView.as_view(), name='auth-trajectory'),
]
