from enum import Enum

from django.conf import settings
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models

from choices import FLAG_REASON_CHOICES, FlagReason


class Flag(models.Model):
    Reason = FlagReason

    class Status(Enum):
        PENDING = 1
        REJECTED = 2
        ACCEPTED = 3

    STATUS_CHOICES = (
        (Status.PENDING.value, 'Pending'),
        (Status.REJECTED.value, 'Rejected'),
        (Status.ACCEPTED.value, 'Accepted'),
    )

    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    object = GenericForeignKey()
    object_author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, blank=True, null=True, related_name='%(class)s_object_author')
    handler = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, blank=True, null=True, related_name='%(class)s_handler')
    status = models.IntegerField(choices=STATUS_CHOICES, default=Status.PENDING.value)

    class Meta:
        unique_together = (('content_type', 'object_id'),)

    def __str__(self):
        return '%s<%s>' % (
            self.content_type.__str__(),
            self.object.__str__(),
        )

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        if self.object:
            self.object_author = self.object.author

        return super().save(force_insert, force_update, using, update_fields)

    @property
    def count(self):
        return self.comment_set.count()

    @property
    def text(self):
        return self.object.text

    @classmethod
    def add_flag(cls, obj, reporter, reason, comment):
        flag, _ = cls.objects.get_or_create(
            content_type=ContentType.objects.get_for_model(obj),
            object_id=obj.pk
        )
        if isinstance(reason, FlagReason):
            reason = reason.value

        return flag.comment_set.create(reporter=reporter, reason=reason, comment=comment)


class FlagComment(models.Model):
    Reason = FlagReason

    object = models.ForeignKey(Flag, on_delete=models.CASCADE, related_name='comment_set')
    reporter = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    created = models.DateTimeField(auto_now_add=True)
    spite = models.BooleanField(default=False)
    reason = models.IntegerField(choices=FLAG_REASON_CHOICES, blank=True, null=True)
    comment = models.TextField(blank=True)

    class Meta:
        unique_together = (('object', 'reporter'),)
