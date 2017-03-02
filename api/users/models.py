from django.db import models

from django.conf import settings


# Create your models here.
class Profile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, unique=True)
    avatar = models.ImageField(upload_to='avatar/', null=True, blank=True, default=None)
    bio = models.TextField(blank=True, default="")

    def __str__(self):
        return self.user.username
