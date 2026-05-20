from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .admin_large_table import LargeTableAdminMixin
from .models import User, UserLocation


@admin.register(User)
class UserAdmin(LargeTableAdminMixin, BaseUserAdmin):
    """Admin volumétrique : pagination sans COUNT(*) global."""

    ordering = ('-id',)
    list_display = (
        'id', 'username', 'email', 'role', 'age', 'region',
        'organization', 'is_active', 'date_joined',
    )
    list_filter = ('role', 'is_active')
    search_fields = ('=id', '=username', '=email', '^username')
    filter_horizontal = ('groups', 'user_permissions')
    readonly_fields = ('last_login', 'date_joined')

    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        (
            'Informations personnelles',
            {'fields': ('first_name', 'last_name', 'email')},
        ),
        ('SIG Sols', {
            'fields': (
                'role', 'organization', 'phone', 'pseudonym',
                'age', 'gender', 'city', 'region', 'profession',
                'education_level', 'motivation', 'consent_analytics',
            ),
        }),
        ('Permissions', {
            'fields': (
                'is_active', 'is_staff', 'is_superuser',
                'groups', 'user_permissions',
            ),
        }),
        ('Dates importantes', {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'password1', 'password2'),
        }),
        ('Informations personnelles', {
            'fields': ('first_name', 'last_name', 'email'),
        }),
        ('SIG Sols', {
            'fields': ('role', 'organization', 'phone', 'age', 'region'),
        }),
    )


@admin.register(UserLocation)
class UserLocationAdmin(LargeTableAdminMixin, admin.ModelAdmin):
    """Positions GPS en temps réel."""

    ordering = ('-updated_at',)
    list_display = ('id', 'user', 'is_sharing', 'accuracy_m', 'updated_at')
    list_filter = ('is_sharing',)
    list_select_related = ('user',)
    raw_id_fields = ('user',)
    readonly_fields = ('updated_at',)
    search_fields = ('=user__pk', '=user__username')
