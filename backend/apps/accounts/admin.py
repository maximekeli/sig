from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _

from config.admin_large_table import LargeTableAdminMixin

from .models import User, UserLocation


@admin.register(User)
class UserAdmin(LargeTableAdminMixin, BaseUserAdmin):
    """
    Admin utilisable avec ~10M d'utilisateurs :
    pas de COUNT(*) global, recherche par clé exacte / préfixe indexé.
    """

    ordering = ('-id',)
    list_display = (
        'id', 'username', 'email', 'role', 'age', 'region',
        'organization', 'is_active', 'date_joined',
    )
    list_filter = ('role', 'is_active')
    list_select_related = ()
    search_fields = ('=id', '=username', '=email', '^username')

    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        (_('Personal info'), {'fields': ('first_name', 'last_name', 'email')}),
        (_('SIG Sols'), {
            'fields': (
                'role', 'organization', 'phone', 'pseudonym',
                'age', 'gender', 'city', 'region', 'profession',
                'education_level', 'motivation', 'consent_analytics',
            ),
        }),
        (_('Permissions'), {
            'fields': (
                'is_active', 'is_staff', 'is_superuser',
                'groups', 'user_permissions',
            ),
        }),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'password1', 'password2'),
        }),
        (_('SIG Sols'), {
            'fields': (
                'role', 'organization', 'phone', 'email',
                'first_name', 'last_name', 'age', 'region',
            ),
        }),
    )


@admin.register(UserLocation)
class UserLocationAdmin(LargeTableAdminMixin, admin.ModelAdmin):
    ordering = ('-updated_at',)
    list_display = ('id', 'user', 'is_sharing', 'accuracy_m', 'updated_at')
    list_filter = ('is_sharing',)
    list_select_related = ('user',)
    raw_id_fields = ('user',)
    readonly_fields = ('updated_at',)
    search_fields = ('=user__id', '=user__username')
