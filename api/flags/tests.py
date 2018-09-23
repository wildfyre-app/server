import unittest
import django
from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model

from areas.models import Area, Post, Comment
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
