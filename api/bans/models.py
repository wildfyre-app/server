from enum import Enum

from django.conf import settings
from django.db import models
from django.db.models import Q
from django.utils import timezone

from choices import BanReason, BAN_REASON_CHOICES


class Action(Enum):
    Posting = 1
    Commenting = 2
    Flagging = 3


class BanBase(models.Model):
    Reason = BanReason

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)

    reason = models.IntegerField(choices=BAN_REASON_CHOICES, blank=True, null=True)
    comment = models.TextField(blank=True)

    auto = models.BooleanField(default=False)

    class Meta:
        abstract = True

    def __str__(self):
        return "%s: %s" % (self.user.username, BanReason(self.reason).name.lower())


class ActiveBanManager(models.Manager):
    """
    Returns only active bans.
    """
    def get_queryset(self):
        return super().get_queryset().filter(
            Q(expiry__gt=timezone.now()) | Q(expiry=None),
            unbanned=False)

    def _may(self, action, user):
        return not self.get_queryset().filter(
            Q(**{'ban_' + action: True}) | Q(ban_all=True),
            user=user).exists()

    def may_post(self, user):
        return self._may('post', user)

    def may_comment(self, user):
        return self._may('comment', user)

    def may_flag(self, user):
        return self._may('flag', user)


class BanActionsMixin(models.Model):
    ban_all = models.BooleanField(default=False)
    ban_post = models.BooleanField(default=False)
    ban_comment = models.BooleanField(default=False)
    ban_flag = models.BooleanField(default=False)

    class Meta:
        abstract = True

    ban_all.short_description = 'Full Ban'


class Ban(BanBase, BanActionsMixin):
    expiry = models.DateTimeField(blank=True, null=True)
    unbanned = models.BooleanField(default=False)

    objects = models.Manager()
    active = ActiveBanManager()

    def _duration(self):
        """
        The duration of the ban.
        None if the ban is permanent.
        """
        if self.expiry is None:
            return self.expiry

        start = self.timestamp or timezone.now()  # If model isn't saved use current time
        return self.expiry - start

    duration = property(_duration)

    expiry.empty_value_display = 'Never'
    _duration.short_description = 'duration'
    _duration.empty_value_display = 'Permanent'


class Warn(BanBase):
    pass
