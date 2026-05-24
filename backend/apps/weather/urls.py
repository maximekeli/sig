from django.urls import path

from .views import OpenWeatherCurrentView, OpenWeatherForecastView, OpenWeatherStatusView

urlpatterns = [
    path('status/', OpenWeatherStatusView.as_view(), name='weather-status'),
    path('current/', OpenWeatherCurrentView.as_view(), name='weather-current'),
    path('forecast/', OpenWeatherForecastView.as_view(), name='weather-forecast'),
]
