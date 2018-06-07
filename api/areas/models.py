import os
import uuid
from random import randint, sample

from django.conf import settings
from django.db import models
from django.db.models import F
from django.utils import timezone

from .registry import registry


def image_path(instance, filename):
    return 'images/%u%s' % (uuid.uuid4(), os.path.splitext(filename)[1])


class PostManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(draft=False)


class Post(models.Model):
    def generate_nonce():
        # Random number from 10000000 to 99999999 (8 digits)
        # Will never start with 0
        return randint(10**7, 10**8-1)

    area = models.CharField(max_length=30, db_index=True)
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=False)  # Might be null, but must only when user gets deleted
    anonym = models.BooleanField(default=False)
    nonce = models.IntegerField(default=generate_nonce)  # To prevent malicious users from trying pk's
    created = models.DateTimeField(default=timezone.now)
    draft = models.BooleanField(default=False, db_index=True)
    active = models.BooleanField(default=False, db_index=True)
    text = models.TextField()
    image = models.ImageField(upload_to=image_path, null=True, blank=True, default=None)

    # Post stack
    stack_outstanding = models.IntegerField(default=0)
    stack_assigned = models.ManyToManyField(settings.AUTH_USER_MODEL, db_index=True, related_name='%(class)s_assigned')
    stack_done = models.ManyToManyField(settings.AUTH_USER_MODEL, db_index=True, related_name='%(class)s_done')

    subscriber = models.ManyToManyField(settings.AUTH_USER_MODEL, blank=True, related_name='%(class)s_subscriber')

    objects = PostManager()
    all_objects = models.Manager()

    class Meta:
        ordering = ['pk']

    def __str__(self):
        return "%s/%s" % (self.area, self.get_uri_key())

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        new = self.pk is None

        if self.area not in registry.areas:
            raise ValueError("'%s' is not a valid Area" % self.area)
        if new and not self.draft:
            self.activate()
        super().save(force_insert, force_update, using, update_fields)
        if new:
            self.stack_done.add(self.author)
            self.subscriber.add(self.author)

    def activate(self):
        self.draft = False
        self.created = timezone.now()
        self.active = True
        self.stack_outstanding = self.get_spread(self.area, self.author)

    def get_uri_key(self):
        """
        Returns the key to use in the uri (nonce + pk)
        """
        return str(self.nonce) + str(self.pk)

    def get_profile(self):
        """
        Returns the profile of the author or None if anonym is True
        """
        if self.anonym or self.author is None:
            return None
        return self.author.profile

    def publish(self):
        if not self.draft:
            raise ValueError("%s is not a draft." % self)

        self.activate()

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

    @staticmethod
    def get_spread(area, user):
        return registry.get_area(area).rep_model.get_spread(area, user).spread

    # Short description for admin
    get_uri_key.short_description = 'id'


class PostImage(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='additional_images')
    num = models.IntegerField()
    image = models.ImageField(upload_to=image_path)
    comment = models.CharField(max_length=128, blank=True, default="")

    MAX_NUM = 4

    class Meta:
        ordering = ['num']
        unique_together = ('post', 'num')


class Comment(models.Model):
    """
    Model for Comments. Can only be used when the default Post Model is used
    """
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    created = models.DateTimeField(auto_now_add=True)
    text = models.TextField()
    image = models.ImageField(upload_to=image_path, null=True, blank=True, default=None)

    unread = models.ManyToManyField(settings.AUTH_USER_MODEL, blank=True, related_name='%(class)s_unread')

    class Meta:
        ordering = ['created']

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
