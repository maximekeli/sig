from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from config.admin_large_table import LargeTableAdminMixin

from .models import User, UserLocation


@admin.register(User)
class UserAdmin(LargeTableAdminMixin, BaseUserAdmin):
    """
    Admin utilisable avec ~10M d'utilisateurs :
    pas de COUNT(*) global, recherche par clé exacte / préfixe indexé.
    """

    ordering = ('-id',)
    list_display = ('id', 'username', 'email', 'role', 'organization', 'is_active', 'date_joined')
    list_filter = ('role', 'is_active')
    list_select_related = ()
    # =id / =email / =username : lookup indexé ; ^username : préfixe (index btree)
    search_fields = ('=id', '=username', '=email', '^username')
    fieldsets = (
        *tuple(BaseUserAdmin.fieldsets or ()),
        ('SIG Sols', {
            'fields': (
                'role', 'organization', 'phone', 'pseudonym',
                'age', 'gender', 'city', 'region', 'profession',
                'education_level', 'motivation', 'consent_analytics',
            ),
        }),
    )
    add_fieldsets = (
        *tuple(BaseUserAdmin.add_fieldsets or ()),
        ('SIG Sols', {'fields': ('role', 'organization')}),
    )


@admin.register(UserLocation)
class UserLocationAdmin(LargeTableAdminMixin, admin.ModelAdmin):
    ordering = ('-updated_at',)
    list_display = ('user_id', 'user', 'is_sharing', 'accuracy_m', 'updated_at')
    list_filter = ('is_sharing',)
    list_select_related = ('user',)
    raw_id_fields = ('user',)
    readonly_fields = ('updated_at',)
    search_fields = ('=user__id', '=user__username')
