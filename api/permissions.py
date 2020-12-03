from rest_framework.permissions import BasePermission, SAFE_METHODS
from .models import User


class IsAdminOrReadOnly(BasePermission):

    def has_permission(self, request, view):
        return bool(
            request.method in SAFE_METHODS or
            request.user and request.user.is_authenticated and
            request.user.is_admin() or
            request.user.is_superuser)


class IsOwnerOrAdmin(BasePermission):

    def has_object_permission(self, request, view, obj):
        return bool(
            obj.author == request.user or
            request.user and request.user.is_authenticated and
            request.user.is_admin() or
            request.user.is_superuser)


class IsOwnerOrAllStaff(BasePermission):
    ALLOWED_USER_ROLES = (User.Roles.MODERATOR, User.Roles.ADMIN)

    def has_object_permission(self, request, view, obj):
        return bool(
            obj.author == request.user or
            request.user and request.user.is_authenticated and
            request.user.role in self.ALLOWED_USER_ROLES or
            request.user.is_superuser)
