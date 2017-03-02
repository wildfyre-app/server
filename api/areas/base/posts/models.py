from django.db import models
from django.core.exceptions import ObjectDoesNotExist
from rest_framework import exceptions

from random import randint

from django.conf import settings


class Post(models.Model):
    def generate_nonce():
        return randint(10**7, 10**8-1)

    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='%(app_label)s_%(class)s')
    nonce = models.IntegerField(default=generate_nonce)  # To prevent malicious users from trying pk's
    created = models.DateTimeField(auto_now_add=True)
    active = models.BooleanField(default=True)
    text = models.TextField()

    # Post stack
    stack_count = models.IntegerField()  # Cards available to be assigned
    stack_assigned = models.ManyToManyField(settings.AUTH_USER_MODEL, db_index=True, related_name='%(app_label)s_%(class)s_assigned')
    stack_done = models.ManyToManyField(settings.AUTH_USER_MODEL, db_index=True, related_name='%(app_label)s_%(class)s_done')

    stack_size = 10  # Maimum cards to assign to one user

    # Short descriptions for admin
    stack_count.short_description = 'In Stack'

    reputation_class = None

    def __str__(self):
        return self.get_uri_key()

    @classmethod
    def get_stack(cls, user):
        """
        Get the current posts stack of one user.
        If the stack is not full this fillis it up
        """
        # Anonymous user cannot have assigned stack
        if not user.is_authenticated():
            raise exceptions.NotAuthenticated()

        obj = cls.objects.filter(stack_assigned__pk=user.pk)

        missing = cls.stack_size - obj.count()
        if missing > 0:
            available = cls.objects.filter(active=True, stack_count__gt=0)
            available = available.exclude(pk__in=obj.values('pk'))  # Exclude allready assined
            available = available.exclude(pk__in=cls.objects.filter(stack_done__pk=user.pk))  # Exclude allready done

            for x in range(0, missing):
                count = available.count()
                if count < 1:
                    # There are no more cards available
                    break

                index = randint(0, count - 1)
                post = available[index]

                available.exclude(pk=post.pk)  # Exclude assigned card, so it does not get chosen again

                post.stack_count -= 1
                post.stack_assigned.add(user)
                post.save()

        return obj

    def get_uri_key(self):
        """
        Returns the key to use in the uri (nonce + pk)
        """
        return str(self.nonce) + str(self.pk)

    get_uri_key.short_description = 'id'

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        if self.stack_count is None:
            # New data set
            try:
                self.stack_count = self.get_reputation(self.author).spread
            except ObjectDoesNotExist:
                # User has no reputation, using 4 as initial spread
                self.stack_count = 4

            resp = super().save(force_insert, force_update, using, update_fields)

            self.stack_done.add(self.author)
            return resp
        return super().save(force_insert, force_update, using, update_fields)

    def get_reputation(self, user):
        assert self.reputation_class is not None, (
            "'%s' should either include a `reputation_class` attribute, "
            "or override the `get_reputation()` method."
            % self.__class__.__name__
            )

        obj, created = self.reputation_class.objects.get_or_create(user=user)
        return obj

    class Meta:
        abstract = True


class Comment(models.Model):
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='%(app_label)s_%(class)s')
    created = models.DateTimeField(auto_now_add=True)
    text = models.TextField()

    class Meta:
        abstract = True
