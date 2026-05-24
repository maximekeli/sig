from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

from config.api_schema import api_schema
from config.health import health_check


urlpatterns = [
    path('health/', health_check),
    path('api/schema/', api_schema),
    path('admin/', admin.site.urls),
    path('api/v1/auth/', include('accounts.urls')),
    path('api/v1/', include('soils.urls')),
    path('api/v1/spatial/', include('spatial.urls')),
    path('api/v1/nasa/', include('nasa.urls')),
    path('api/v1/sentinel/', include('sentinel.urls')),
    path('api/v1/ml/', include('ml_predict.urls')),
    path('api/v1/education/', include('education.urls')),
    path('api/v1/platform/', include('sig_platform.urls')),
    path('api/v1/assistant/', include('assistant.urls')),
    path('api/v1/videos/', include('videos.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
