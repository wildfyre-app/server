from django.db import models

from django.contrib.auth.models import User


# Create your models here.
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, unique=True)
    avatar = models.ImageField(upload_to='avatar/', null=True, blank=True, default=None)
    bio = models.TextField(blank=True, default="")

    def __str__(self):
        return self.user.username
