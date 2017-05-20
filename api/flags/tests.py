import unittest
import django
from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model

from .models import Flag


class FlagTest(TestCase):
    def test_flag(self):
        """
        Try to flag some content (a User in this case)
        """
        obj = get_user_model().objects.create(username="someUser")
        reporter = get_user_model().objects.create(username="reporter")
        flag = Flag.add_flag(obj, reporter, Flag.Reason.RUDE, "")

        # No error, everything seems fine
