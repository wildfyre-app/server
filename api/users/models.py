import os

from django.db import models
from django.core.exceptions import ObjectDoesNotExist

from django.conf import settings
from django.contrib.auth import get_user_model


class ProfileQuerySet(models.QuerySet):
    def get(self, *args, **kwargs):
        """
        Gets the profile. If it doesn't exist it is created
        """
        lookup, params = self._extract_model_params(None, **kwargs)
        try:
            return super().get(**lookup)
        except self.model.DoesNotExist:
            user = lookup.get(
                'user',
                lookup.get(
                    'user__id',
                    lookup.get(
                        'user__pk',
                        lookup.get(
                            'user_id'
                            )
                        )
                    )
                )
            # If user is int convert it to User object
            try:
                int(user)
            except TypeError:
                pass
            else:
                try:
                    user = get_user_model().objects.get(pk=user)
                except ObjectDoesNotExist:
                    raise self.model.DoesNotExist("User matching query does not exist.")
            return self.create(user=user)


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
