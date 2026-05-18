from django.urls import path

from .views import (
    AdminDashboardView,
    AuditLogListView,
    DroughtAlertListView,
    NotificationListView,
    NotificationMarkReadView,
    PasswordResetConfirmView,
    PasswordResetRequestView,
    ZoneReportView,
)

urlpatterns = [
    path('admin/dashboard/', AdminDashboardView.as_view(), name='admin-dashboard'),
    path('notifications/', NotificationListView.as_view(), name='notifications'),
    path('notifications/<int:pk>/read/', NotificationMarkReadView.as_view(), name='notification-read'),
    path('alerts/drought/', DroughtAlertListView.as_view(), name='drought-alerts'),
    path('audit/', AuditLogListView.as_view(), name='audit-log'),
    path('password/reset/', PasswordResetRequestView.as_view(), name='password-reset'),
    path('password/reset/confirm/', PasswordResetConfirmView.as_view(), name='password-reset-confirm'),
    path('reports/zone/<str:zone_code>/', ZoneReportView.as_view(), name='zone-report'),
]
