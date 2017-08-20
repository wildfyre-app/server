from rest_framework import permissions

from .models import Ban


class MayBase(permissions.BasePermission):
    """
    Base class for ban checks
    """
    def has_permission(self, request, view):
        # Allow safe methods
        if request.method in permissions.SAFE_METHODS:
            return True

        return self.may(request, view)

    def may(self, request, view):
        raise NotImplementedError()


class MayPost(MayBase):
    """
    Check if user is allowed to post
    """
    def may(self, request, view):
        return Ban.active.may_post(request.user)


class MayComment(MayBase):
    """
    Check if user is allowed to comment
    """
    def may(self, request, view):
        return Ban.active.may_comment(request.user)


class MayFlag(MayBase):
    """
    Check if user is allowed to falg
    """
    def may(self, request, view):
        return Ban.active.may_flag(request.user)


class MayFlagPost(MayFlag):
    """
    Check if user is allowed to flag post
    """
    pass


class MayFlagComment(MayFlag):
    """
    Check if user is allowed to flag comment
    """
    pass
