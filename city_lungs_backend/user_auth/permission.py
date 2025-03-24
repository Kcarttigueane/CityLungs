from rest_framework import permissions


class IsAdmin(permissions.BasePermission):
    """
    Permission check for administrators only.
    """
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.is_admin())


class IsCitizen(permissions.BasePermission):
    """
    Permission check for citizens (regular users).
    """
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.is_citizen())


class IsAdminOrReadOnly(permissions.BasePermission):
    """
    Permission check for admin write access, but allow read access to any authenticated user.
    """
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return bool(request.user and request.user.is_authenticated)
        return bool(request.user and request.user.is_authenticated and request.user.is_admin())


class IsOwnerOrAdmin(permissions.BasePermission):
    """
    Object-level permission to only allow owners of an object or admins to edit it.
    Assumes the model instance has an `user` attribute.
    """
    def has_object_permission(self, request, view, obj):
        if request.user.is_admin():
            return True
        
        # Assuming 'user' is a field on the object
        return obj.user == request.user