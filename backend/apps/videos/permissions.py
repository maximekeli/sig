from rest_framework.permissions import BasePermission, SAFE_METHODS

from accounts.models import User

from .services import user_can_view_post


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
            return user_can_view_post(obj, user)
        if not isinstance(user, User) or not user.is_authenticated:
            return False
        if getattr(view, 'action', None) in (
            'approve', 'reject', 'feature', 'toggle_like', 'comments',
        ):
            if view.action in ('approve', 'reject', 'feature'):
                return user.is_administrator
            if view.action == 'toggle_like':
                return user_can_view_post(obj, user)
            if view.action == 'comments' and request.method == 'GET':
                return user_can_view_post(obj, user)
            if view.action == 'comments' and request.method == 'POST':
                return user_can_view_post(obj, user)
        if request.method in ('PUT', 'PATCH', 'DELETE'):
            return obj.author_id == user.pk or user.is_administrator
        return True


class VideoCommentPermission(BasePermission):
    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True
        return (
            isinstance(request.user, User)
            and request.user.is_authenticated
        )

    def has_object_permission(self, request, view, obj):
        user = request.user
        if request.method in SAFE_METHODS:
            return user_can_view_post(obj.post, user)
        if not isinstance(user, User) or not user.is_authenticated:
            return False
        if getattr(view, 'action', None) == 'toggle_like':
            return user_can_view_post(obj.post, user)
        if request.method == 'DELETE':
            return obj.author_id == user.pk or user.is_administrator
        return False
