from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.http import JsonResponse
from django.urls import include, path


def health_check(_request):
    return JsonResponse({'status': 'ok', 'project': 'SIG-SOLS-TOGO-2026-01'})


urlpatterns = [
    path('health/', health_check),
    path('admin/', admin.site.urls),
    path('api/v1/auth/', include('accounts.urls')),
    path('api/v1/', include('soils.urls')),
    path('api/v1/spatial/', include('spatial.urls')),
    path('api/v1/nasa/', include('nasa.urls')),
    path('api/v1/ml/', include('ml_predict.urls')),
    path('api/v1/education/', include('education.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
