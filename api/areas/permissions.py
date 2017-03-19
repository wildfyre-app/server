from rest_framework import permissions


class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Only allow the owner of a post or comment to edit/delete it
    """
    def has_object_permission(self, request, view, obj):
        # Allow safe methods
        if request.method in permissions.SAFE_METHODS:
            return True

        # Write permission only to owner
        return obj.author == request.user


class IsOwnerOrReadCreateOnly(IsOwnerOrReadOnly):
    """
    Allow others to create sub objects (comments)
    """
    def has_object_permission(self, request, view, obj):
        # Allow POST
        if request.method == 'POST':
            return True

        return super().has_object_permission(request, view, obj)


class IsInStack(permissions.BasePermission):
    """
    Only allow access if the card is in the users stack
    """
    def has_object_permission(self, request, view, obj):
        return obj.stack_assigned.filter(pk=request.user.pk).exists()
