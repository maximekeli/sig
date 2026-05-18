from django.contrib import admin

from .models import AuditLog, DroughtAlert, Notification, PasswordResetToken


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
