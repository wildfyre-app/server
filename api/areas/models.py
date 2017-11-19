from random import randint, sample

from django.conf import settings
from django.db import models
from django.db.models import F

from .registry import registry


class Post(models.Model):
    def generate_nonce():
        # Random number from 10000000 to 99999999 (8 digits)
        # Will never start with 0
        return randint(10**7, 10**8-1)

    area = models.CharField(max_length=30, db_index=True)
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=False)  # Might be null, but must only when user gets deleted
    nonce = models.IntegerField(default=generate_nonce)  # To prevent malicious users from trying pk's
    created = models.DateTimeField(auto_now_add=True)
    active = models.BooleanField(default=True)
    text = models.TextField()

    # Post stack
    stack_outstanding = models.IntegerField()
    stack_assigned = models.ManyToManyField(settings.AUTH_USER_MODEL, db_index=True, related_name='%(class)s_assigned')
    stack_done = models.ManyToManyField(settings.AUTH_USER_MODEL, db_index=True, related_name='%(class)s_done')

    subscriber = models.ManyToManyField(settings.AUTH_USER_MODEL, blank=True, related_name='%(class)s_subscriber')

    def __str__(self):
        return self.get_uri_key()

    def get_uri_key(self):
        """
        Returns the key to use in the uri (nonce + pk)
        """
        return str(self.nonce) + str(self.pk)

    @classmethod
    def get_stack(cls, area, user):
        """
        Fills up the stack of the user and returns it
        """
        stack = cls.objects.filter(area=area.name, stack_assigned__pk=user.pk)

        missing = area.max_user_stack - stack.count()
        if missing > 0:
            available = cls.objects.filter(active=True, area=area.name, stack_outstanding__gt=0)
            available = available.exclude(pk__in=stack.values('pk'))  # Exclude allready assined
            available = available.exclude(pk__in=cls.objects.filter(stack_done__pk=user.pk))  # Exclude already done

            numAvailable = len(available)  # Evaluate queryset. To avoid race conditions (less available than count)
            if numAvailable <= missing:
                # When there are not more cards available than missing take all
                for post in available:
                    post.assign_user(user)
            else:
                for index in sample(range(numAvailable), missing):
                    available[index].assign_user(user)

        return stack

    def assign_user(self, user):
        self.stack_outstanding = F('stack_outstanding') - 1
        self.stack_assigned.add(user)
        self.save()
        self.refresh_from_db()

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        new = self.pk is None

        if self.area not in registry.areas:
            raise ValueError("'%s' is not a valid Area" % self.area)
        if new:
            self.stack_outstanding = self.get_spread(self.area, self.author)
        super().save(force_insert, force_update, using, update_fields)
        if new:
            self.stack_done.add(self.author)
            self.subscriber.add(self.author)

    @staticmethod
    def get_spread(area, user):
        return registry.get_area(area).rep_model.get_spread(area, user).spread

    # Short description for admin
    get_uri_key.short_description = 'id'


class Comment(models.Model):
    """
    Model for Comments. Can only be used when the default Post Model is used
    """
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    created = models.DateTimeField(auto_now_add=True)
    text = models.TextField()

    unread = models.ManyToManyField(settings.AUTH_USER_MODEL, blank=True, related_name='%(class)s_unread')

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        new = self.pk is None
        super().save(force_insert, force_update, using, update_fields)
        if new:
            self.post.subscriber.add(self.author.pk)  # Ensure comment author is subscribed
            subscriber = self.post.subscriber.exclude(pk=self.author.pk)
            self.unread.add(*subscriber)

    def __str__(self):
        return "%s/%s" % (self.post, self.pk)


class Reputation(models.Model):
    area = models.CharField(max_length=30, db_index=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    reputation = models.IntegerField(default=0)

    def __str__(self):
        return '%s/%s: %s (%s)' % (self.area, self.user, self.reputation, self.spread)

    @property
    def spread(self):
        # Calculate Spread amount:
        # (3rd root of 3*rep) + 3
        spread = int((3 * self.reputation) ** (1 / 3) + 3)
        min = registry.get_area(self.area).spread_min
        if spread < min:
            spread = min
        return spread

    @classmethod
    def get_spread(cls, area, user):
        return cls.objects.get_or_create(area=area, user=user)[0]

    class Meta:
        unique_together = (('area', 'user'),)
