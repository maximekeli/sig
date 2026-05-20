from django.contrib import admin

from accounts.admin_large_table import LargeTableAdminMixin

from .models import VideoPost


@admin.register(VideoPost)
class VideoPostAdmin(LargeTableAdminMixin, admin.ModelAdmin):
    list_display = (
        'id', 'title', 'kind', 'status', 'author',
        'is_featured', 'view_count', 'created_at',
    )
    list_filter = ('kind', 'status', 'is_featured')
    search_fields = ('=id', '=title', 'author__username')
    raw_id_fields = ('author', 'moderated_by')
    readonly_fields = (
        'view_count', 'moderated_at', 'created_at', 'updated_at',
    )
    list_select_related = ('author',)
    actions = ['approve_selected', 'reject_selected']

    @admin.action(description='Publier la sélection')
    def approve_selected(self, request, queryset):
        from django.utils import timezone

        queryset.update(
            status=VideoPost.Status.PUBLISHED,
            rejection_reason='',
            moderated_by=request.user,
            moderated_at=timezone.now(),
        )

    @admin.action(description='Refuser la sélection')
    def reject_selected(self, request, queryset):
        from django.utils import timezone

        queryset.update(
            status=VideoPost.Status.REJECTED,
            rejection_reason='Refusé depuis l’admin Django.',
            moderated_by=request.user,
            moderated_at=timezone.now(),
        )
