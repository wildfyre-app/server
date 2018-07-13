from django.core.exceptions import ValidationError
from django.db import models

from django.contrib.auth.models import AbstractUser, UserManager


class UserManager(UserManager):
    def get_by_natural_key(self, username):
        username_field = self.model.USERNAME_FIELD
        return self.get(**{username_field + '__iexact': username})


class User(AbstractUser):
    objects = UserManager()

    def validate_unique(self, exclude=None):
        errors = {}
        if exclude is None:
            exclude = []
        else:
            exclude = list(exclude)

        try:
            super().validate_unique(exclude)
        except ValidationError as e:
            errors = e.update_error_dict(errors)

        if not (self.USERNAME_FIELD in exclude or self.USERNAME_FIELD in errors):
            # Check if username is unique case-insensitive
            same_name = self.__class__._default_manager.filter(
                **{self.USERNAME_FIELD + '__iexact': getattr(self, self.USERNAME_FIELD)})
            if same_name.exists() and same_name.get().pk != self.pk:
                errors.update(
                    {self.USERNAME_FIELD: self.unique_error_message(self.__class__, (self.USERNAME_FIELD,))}
                )

        if errors:
            raise ValidationError(errors)
