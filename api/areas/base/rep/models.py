from django.db import models

from django.conf import settings


class Reputation(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='%(app_label)s_%(class)s')
    reputation = models.IntegerField(default=0)
    spread = models.IntegerField()

    min_spread = 4

    def __str__(self):
        return str(self.reputation) + ' (' + str(self.spread) + ')'

    @classmethod
    def get_spread(cls, user):
        obj = cls.objects.all(user=user)
        return obj.spread

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        # Calculate Spread amount:
        # (3rd root of 3*rep) + 3
        self.spread = int((3 * self.reputation) ** (1 / 3) + 3)
        if self.spread < self.min_spread:
            self.spread = self.min_spread

        return super().save(force_insert, force_update, using, update_fields)

    class Meta:
        abstract = True
