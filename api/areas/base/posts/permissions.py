from rest_framework import permissions


class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Only allow the owner of an object to edit it
    """

    def has_object_permission(self, request, view, obj):
        # Allow safe methods
        if request.method in permissions.SAFE_METHODS:
            return True

        # Write permissions only to owner
        return obj.author == request.user
