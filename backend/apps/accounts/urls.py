from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView

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
    path('register/', RegisterView.as_view(), name='auth-register'),
    path('token/', TokenObtainView.as_view(), name='token-obtain'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token-refresh'),
    path('logout/', LogoutView.as_view(), name='auth-logout'),
    path('profile/', ProfileView.as_view(), name='auth-profile'),
    path('profile/photo/', ProfilePhotoView.as_view(), name='auth-profile-photo'),
    path('password/change/', ChangePasswordView.as_view(), name='auth-password-change'),
    path('users/', UserListView.as_view(), name='auth-users'),
    path('location/', MyLocationView.as_view(), name='auth-location'),
    path('locations/live/', LiveLocationsView.as_view(), name='auth-locations-live'),
    path('trajectory/', UserTrajectoryView.as_view(), name='auth-trajectory-self'),
    path('trajectory/<int:user_id>/', UserTrajectoryView.as_view(), name='auth-trajectory'),
]
