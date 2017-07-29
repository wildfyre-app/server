from rest_framework import permissions

from bans.models import Ban


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
        if (obj.__class__ == type):
            # Anonymous object for this user
            return True
        return obj.stack_assigned.filter(pk=request.user.pk).exists()


class MayPost(permissions.BasePermission):
    """
    Check if user is allowed to post
    """
    def has_object_permission(self, request, view, obj):
        # Allow safe methods
        if request.method in permissions.SAFE_METHODS:
            return True

        return Ban.active.may_post(request.user)


class MayComment(permissions.BasePermission):
    """
    Check if user is allowed to comment
    """
    def has_object_permission(self, request, view, obj):
        # Allow safe methods
        if request.method in permissions.SAFE_METHODS:
            return True

        return Ban.active.may_comment(request.user)


class MayFlag(permissions.BasePermission):
    """
    Check if user is allowed to falg
    """
    def has_object_permission(self, request, view, obj):
        # Allow safe methods
        if request.method in permissions.SAFE_METHODS:
            return True

        return Ban.active.may_flag(request.user)


class MayFlagPost(MayFlag):
    """
    Check if user is allowed to flag post
    """
    def has_object_permission(self, request, view, obj):
        return super().has_object_permission(request, view, obj)


class MayFlagComment(MayFlag):
    """
    Check if user is allowed to flag comment
    """
    def has_object_permission(self, request, view, obj):
        return super().has_object_permission(request, view, obj)
