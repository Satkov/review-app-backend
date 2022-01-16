from rest_framework.permissions import SAFE_METHODS, BasePermission


class IsCurrentUserOrAdminOrReadOnly(BasePermission):
    """
    Custom permission to only allow owners of an object to edit it.
    """
    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS or obj.is_superuser:
            return True
        return obj == request.user
