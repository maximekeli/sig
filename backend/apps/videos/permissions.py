from rest_framework.permissions import BasePermission, SAFE_METHODS

from accounts.models import User


class VideoPostPermission(BasePermission):
    """
    Lecture : publications publiées, ou les siennes (tout statut).
    Écriture : utilisateurs connectés ; modération réservée aux admins.
    """

    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True
        user = request.user
        return isinstance(user, User) and user.is_authenticated

    def has_object_permission(self, request, view, obj):
        user = request.user
        if request.method in SAFE_METHODS:
            if obj.status == obj.Status.PUBLISHED:
                return True
            return (
                isinstance(user, User)
                and user.is_authenticated
                and (obj.author_id == user.pk or user.is_administrator)
            )
        if not isinstance(user, User) or not user.is_authenticated:
            return False
        if getattr(view, 'action', None) in ('approve', 'reject', 'feature'):
            return user.is_administrator
        if request.method in ('PUT', 'PATCH', 'DELETE'):
            return obj.author_id == user.pk or user.is_administrator
        return True
