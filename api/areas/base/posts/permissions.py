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


class IsOwnerOrReadCreateOnly(IsOwnerOrReadOnly):
    """
    Only allow the owner of an object to edit it.
    Allow everyone to comment on it
    """

    def has_object_permission(self, request, view, obj):
        # Allow Creating Comments
        if request.method == 'POST':
            return True
        return super().has_object_permission(request, view, obj)
