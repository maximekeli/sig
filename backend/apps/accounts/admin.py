from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .models import User, UserLocation


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ('username', 'email', 'role', 'organization', 'is_active')
    list_filter = ('role', 'is_staff', 'is_active')
    fieldsets = BaseUserAdmin.fieldsets + (
        ('SIG Sols', {'fields': ('role', 'organization', 'phone', 'pseudonym')}),
    )
    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        ('SIG Sols', {'fields': ('role', 'organization')}),
    )


@admin.register(UserLocation)
class UserLocationAdmin(admin.ModelAdmin):
    list_display = ('user', 'is_sharing', 'accuracy_m', 'updated_at')
    list_filter = ('is_sharing', 'updated_at')
    readonly_fields = ('updated_at',)
