import datetime
import uuid
from secrets import token_urlsafe

from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.db import models
from django.utils import timezone

from . import send_mail


def token_default():
    return token_urlsafe(50)  # Requires at max 68 Chars


class ConfirmMail(models.Model):
    token_default = token_default

    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    new_mail = models.EmailField()
    token = models.CharField(max_length=68, default=token_default)
    created = models.DateTimeField(auto_now_add=True)

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        try:
            ConfirmMail.objects.get(user=self.user).delete()
        except ObjectDoesNotExist:
            pass

        returned = super().save(force_insert, force_update, using, update_fields)
        send_mail('confirm', "Please confirm your email", self.new_mail, {
            'username': self.user.username,
            'pk': self.pk,
            'token': self.token,
        })
        return returned


class ResetPassword(models.Model):
    token_default = token_default

    def transaction_default():
        return uuid.uuid4()

    def expire_date_default():
        return timezone.now() + datetime.timedelta(hours=6)

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    transaction = models.UUIDField(default=transaction_default)
    token = models.CharField(max_length=68, default=token_default)
    expire_date = models.DateTimeField(db_index=True, default=expire_date_default)

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        send_mail('passwordreset', "Password reset confirmation", self.user.email, {
            'username': self.user.username,
            'token': self.token
        })
        return super().save(force_insert, force_update, using, update_fields)
