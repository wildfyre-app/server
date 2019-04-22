import os

from django.db import models
from django.db.utils import IntegrityError
from django.conf import settings
from django.contrib.auth import get_user_model


class ProfileQuerySet(models.QuerySet):
    def get(self, *args, **kwargs):
        """
        Gets the profile. If it doesn't exist it is created
        """
        # Use write databse. It's more up to date.
        self._for_write = True
        try:
            return super().get(*args, **kwargs)
        except self.model.DoesNotExist as e:
            user = kwargs.pop("user", kwargs.pop("user__id", None))
            if len(args) != 0 or user is None or len(kwargs) != 0:
                raise e
            else:
                # If user is int convert it to User object
                if isinstance(user, int):
                    try:
                        user = get_user_model().objects.get(pk=user)
                    except get_user_model().DoesNotExist:
                        raise e
                try:
                    return self.create(user=user)
                except IntegrityError:
                    # Someone trying to create the same profile was faster. It should be there now though.
                    return super().get(*args, **kwargs)


class Profile(models.Model):
    def avatar_path(instance, filename):
        return 'avatar/%u%s' % (instance.user.id, os.path.splitext(filename)[1])

    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, unique=True)
    avatar = models.ImageField(upload_to=avatar_path, null=True, blank=True, default=None)
    bio = models.TextField(blank=True, default="")

    objects = ProfileQuerySet.as_manager()

    def __str__(self):
        return self.user.username

    class Meta:
        base_manager_name = 'objects'  # This manager MUST NOT filter anything away!
