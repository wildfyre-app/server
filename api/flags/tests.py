import unittest

import django
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from areas.models import Area, Comment, Post

from .admin import FlagAdmin
from .models import Flag


class FlagTest(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create(username="someUser")
        self.reporter = get_user_model().objects.create(username="reporter")

        self.post = Post.objects.create(author=self.user, text="This is rude", area=Area.objects.create(name='example', displayname="Example Area"))

    def test_flag_post(self):
        """
        Try to flag a post
        """
        flag = Flag.add_flag(self.post, self.reporter, Flag.Reason.RUDE, "")
        # No error, everything seems fine

    def test_flag_comment(self):
        """
        Try to flag a comment
        """
        comment = Comment.objects.create(post=self.post, author=self.user, text="This is evil")
        flag = Flag.add_flag(comment, self.reporter, Flag.Reason.OTHER, "Evil")
        # No error, everything seems fine


class FlagAdminTest(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create(username="someUser")
        self.reporter = get_user_model().objects.create(username="reporter")

        self.post = Post.objects.create(author=self.user, text="This is rude", area=Area.objects.create(name='example', displayname="Example Area"))
        self.post_flag = Flag.add_flag(self.post, self.reporter, Flag.Reason.RUDE, "").object
        self.comment = Comment.objects.create(post=self.post, author=self.user, text="This is evil")
        self.comment_flag = Flag.add_flag(self.comment, self.reporter, Flag.Reason.OTHER, "Evil").object

    def test_url(self):
        """
        Check if the admin can get the edit url to the post
        """
        FlagAdmin.url(None, self.post_flag)
        FlagAdmin.url(None, self.comment_flag)
