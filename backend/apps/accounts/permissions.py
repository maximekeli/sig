from rest_framework.permissions import BasePermission

from .models import User


class IsAdministrator(BasePermission):
    def has_permission(self, request, view):
        user = request.user
        if not isinstance(user, User) or not user.is_authenticated:
            return False
        return user.is_administrator


class IsAgentOrAdmin(BasePermission):
    def has_permission(self, request, view):
        user = request.user
        if not isinstance(user, User) or not user.is_authenticated:
            return False
        return user.is_agent
