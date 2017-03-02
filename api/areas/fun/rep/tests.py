import django
from django.shortcuts import reverse
from django.test import TestCase
from rest_framework.test import APIRequestFactory, force_authenticate

from .views import *
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser


class RepTest(TestCase):
    def setUp(self):
            # We need the test factory for all tests
            self.factory = APIRequestFactory()
            # Test User
            self.user = get_user_model().objects.create_user(
                username='user', password='secret')

    def test_not_authenticated(self):
        """
        Status code 401: Unauthorized should be raised
        """
        request = self.factory.get(reverse('areas:fun:rep:get'))
        request.user = AnonymousUser()
        response = ReputationView.as_view()(request)

        self.assertEqual(response.status_code, 401)

    def test_no_rep(self):
        """
        When User has no Rep, a new Reputation object should be generated for him
        """
        request = self.factory.get(reverse('areas:fun:rep:get'))
        force_authenticate(request, self.user)
        response = ReputationView.as_view()(request)

        self.assertEqual(response.status_code, 200)

    def test_change_rep(self):
        """
        Should respond with 405: Method not allowed
        """
        request = self.factory.patch(reverse('areas:fun:rep:get'), {'reputation': 1000})
        force_authenticate(request, self.user)
        response = ReputationView.as_view()(request)

        self.assertEqual(response.status_code, 405)
