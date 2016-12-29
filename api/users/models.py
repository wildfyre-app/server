from django.db import models

import os
from base64 import urlsafe_b64encode
from django.core.exceptions import ObjectDoesNotExist

from django.core.mail import EmailMultiAlternatives
from django.template.loader import get_template

from django.contrib.auth.models import User
from django.core.mail import send_mail


# Create your models here.
class ConfirmMail(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    new_mail = models.EmailField()
    nonce = models.CharField(max_length=68, blank=True)  # Allow Blank because nonce is generated when saving
    created = models.DateTimeField(auto_now_add=True)

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        try:
            ConfirmMail.objects.get(user=self.user).delete()
        except ObjectDoesNotExist:
            pass

        self.nonce = urlsafe_b64encode(os.urandom(50))  # Requires 68 Chars

        returned = super().save(force_insert, force_update, using, update_fields)

        # Send mail
        context = {'username': self.user.username, 'pk': self.pk, 'nonce': self.nonce}
        mail_plain = get_template('users/mail_confirm.txt').render(context)
        mail_html = get_template('users/mail_confirm.html').render(context)

        subject = "[WildFyre] Please confirm your email"

        msg = EmailMultiAlternatives(subject, mail_plain, "noreply@wildfyre.net", [self.new_mail])
        msg.attach_alternative(mail_html, "text/html")
        msg.send()

        return returned
