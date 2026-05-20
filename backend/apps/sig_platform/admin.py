from django.contrib import admin

from .models import AuditLog, DroughtAlert, Notification, PasswordResetToken, UserActivityEvent


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ('action', 'resource', 'resource_id', 'user', 'created_at')
    list_filter = ('action', 'resource')


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('title', 'user', 'level', 'is_read', 'created_at')


@admin.register(DroughtAlert)
class DroughtAlertAdmin(admin.ModelAdmin):
    list_display = ('soil_point', 'severity', 'is_active', 'created_at')


@admin.register(PasswordResetToken)
class PasswordResetTokenAdmin(admin.ModelAdmin):
    list_display = ('user', 'used', 'created_at')


@admin.register(UserActivityEvent)
class UserActivityEventAdmin(admin.ModelAdmin):
    ordering = ('-created_at',)
    list_display = ('created_at', 'user', 'event_type', 'category', 'view_name', 'session_id')
    list_filter = ('category', 'event_type', 'view_name')
    search_fields = ('=user__id', '=user__username', 'session_id', 'event_type')
    raw_id_fields = ('user',)
    readonly_fields = ('created_at',)
