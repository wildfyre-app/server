"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""

import django
from django.urls import reverse

from django.test import TestCase
from rest_framework.test import APIRequestFactory, force_authenticate

from .views import *
from .models import *
from django.contrib.auth import authenticate
from django.contrib.auth.models import AnonymousUser, User
from rest_framework.authtoken.models import Token
from django.core import mail

class AccountTest(TestCase):

    def setUp(self):
            # We need the test factory for all tests
            self.factory = APIRequestFactory()
            # Test User
            self.user1 = User.objects.create_user(
                username='user1', email='user1@example.invalid', password='secret')

            self.user2 = User.objects.create_user(
                username='user2', email='user2@example.invalid', password='secret')

            self.user_no_email = User.objects.create_user(
                username='user_no_email', password='secret')

    def test_not_authenticated(self):
        """
        Status code 401: Unauthorized should be raised
        """
        request = self.factory.get(reverse('users:account'))
        request.user = AnonymousUser()
        response = AccountView.as_view()(request)

        self.assertEqual(response.status_code, 401)

    def test_password_change_patch(self):
        """
        Changing the user Password with PATCH
        """
        password = "highQualw39Qdjf@♣asdk34kasdUI$E"  # So the test also works when we enforce stronger passwords
        request = self.factory.patch(reverse('users:account'), {'password': password})
        force_authenticate(request, self.user1)
        response = AccountView.as_view()(request)

        self.assertEqual(response.status_code, 200)
        
        user = authenticate(username='user1', password=password)
        self.assertIsNotNone(user)

    def test_change_password_token_invalid(self):
        """
        Changing the user password should invalidate the users token

        This test will fail when moving to another token auth system and should then be replaced
        """
        token = Token.objects.get_or_create(user=self.user1)

        password = "highQualw39Qdjf@♣asdk34kasdUI$E"  # So the test also works when we enforce stronger passwords
        request = self.factory.patch(reverse('users:account'), {'password': password})
        force_authenticate(request, self.user1)
        AccountView.as_view()(request)

        self.assertNotEqual(token, Token.objects.get_or_create(user=self.user1))

    def test_change_id(self):
        """
        Changing the id should fail
        """
        oldid = self.user1.id

        request = self.factory.patch(reverse('users:account'), {'id': 99})
        force_authenticate(request, self.user1)
        response = AccountView.as_view()(request)

        self.assertEqual(oldid, self.user1.id)

class ProfileTest(TestCase):

    def setUp(self):
            # We need the test factory for all tests
            self.factory = APIRequestFactory()
            # Test User
            self.user1 = User.objects.create_user(
                username='user1', email='user1@example.invalid', password='secret')

            self.user2 = User.objects.create_user(
                username='user2', email='user2@example.invalid', password='secret')

            self.user_no_email = User.objects.create_user(
                username='user_no_email', password='secret')

    def test_can_patch(self):
        """
        Users shouldn't be able to change the profile

        Should return 405 Method Not allowed 
        """
        password = "highQualw39Qdjf@♣asdk34kasdUI$E"  # So the test also works when we enforce stronger passwords
        request = self.factory.patch(reverse('users:profile', kwargs={'pk': self.user2.id}), {'password': password})
        force_authenticate(request, self.user1)
        response = ProfileView.as_view()(request)

        self.assertEqual(response.status_code, 405)

    def test_can_delete(self):
        """
        Users may not delete other users
        """
        request = self.factory.delete(reverse('users:profile', kwargs={'pk': self.user2.id}))
        force_authenticate(request, self.user1)
        response = ProfileView.as_view()(request)

        self.assertEqual(response.status_code, 405)

    def test_can_see_email(self):
        """
        Users shouldn't see the email of other users
        """
        request = self.factory.get(reverse('users:profile', kwargs={'pk': self.user2.id}))
        force_authenticate(request, self.user1)
        response = ProfileView.as_view()(request, pk=self.user2.pk)
        response.render()

        self.assertNotContains(response, "email")


class EmailTest(TestCase):

    def setUp(self):
            # We need the test factory for all tests
            self.factory = APIRequestFactory()
            # Test User
            self.user = User.objects.create_user(
                username="user", email="user@example.invalid", password="secret")

    def test_change_mail(self):
        """
        Users should recive an confirmation email if they change their email address
        """
        request = self.factory.patch(reverse('users:account'), {'email': "newmail@example.invalid"})
        force_authenticate(request, self.user)
        response = AccountView.as_view()(request)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(mail.outbox), 1)
        self.assertIsNotNone(ConfirmMail.objects.get(user=self.user))
