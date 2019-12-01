import threading
import unittest

import django
from django.contrib.auth import authenticate, get_user_model
from django.contrib.auth.models import AnonymousUser
from django.core import mail
from django.test import TestCase, override_settings
from django.urls import reverse

from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.test import APIRequestFactory, APITestCase, force_authenticate

from .models import *
from .views import *

RECAPTCHA_TEST_SECRET = "6LeIxAcTAAAAAGG-vFI1TnRWxMZNFuojJ4WifJWe"


def join_all_threads():
    for thread in threading.enumerate():
        thread is threading.current_thread() or thread.join()

class AccountTest(TestCase):

    def setUp(self):
            # We need the test factory for all tests
            self.factory = APIRequestFactory()
            # Test User
            self.user1 = get_user_model().objects.create_user(
                username='user1', email='user1@example.invalid', password='secret')

            self.user2 = get_user_model().objects.create_user(
                username='user2', email='user2@example.invalid', password='secret')

            self.user_no_email = get_user_model().objects.create_user(
                username='user_no_email', password='secret')

    def test_not_authenticated(self):
        """
        Status code 401: Unauthorized should be raised
        """
        request = self.factory.get(reverse('account:account'))
        request.user = AnonymousUser()
        response = AccountView.as_view()(request)

        self.assertEqual(response.status_code, 401)

    def test_password_change_patch(self):
        """
        Changing the user Password with PATCH
        """
        password = "highQualw39Qdjf@♣asdk34kasdUI$E"  # So the test also works when we enforce stronger passwords
        request = self.factory.patch(reverse('account:account'), {'password': password})
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
        request = self.factory.patch(reverse('account:account'), {'password': password})
        force_authenticate(request, self.user1)
        AccountView.as_view()(request)

        self.assertNotEqual(token, Token.objects.get_or_create(user=self.user1))

    def test_change_id(self):
        """
        Changing the id should fail
        """
        oldid = self.user1.id

        request = self.factory.patch(reverse('account:account'), {'id': 99})
        force_authenticate(request, self.user1)
        response = AccountView.as_view()(request)

        self.assertEqual(oldid, self.user1.id)

    def test_change_username(self):
        """
        Changing the username should not be possible
        """
        olduser = self.user1.username

        request = self.factory.patch(reverse('account:account'), {'username': "somethingElse"})
        force_authenticate(request, self.user1)
        response = AccountView.as_view()(request)

        self.assertEqual(olduser, self.user1.username)


class EmailTest(TestCase):

    def setUp(self):
            # We need the test factory for all tests
            self.factory = APIRequestFactory()
            # Test User
            self.user = get_user_model().objects.create_user(
                username="user", email="user@example.invalid", password="secret")

    def test_change_mail(self):
        """
        Users should recive an confirmation email if they change their email address
        """
        request = self.factory.patch(reverse('account:account'), {'email': "newmail@example.invalid"})
        force_authenticate(request, self.user)
        response = AccountView.as_view()(request)

        join_all_threads()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(mail.outbox), 1)
        self.assertIsNotNone(ConfirmMail.objects.get(user=self.user))


@override_settings(RECAPTCHA_SECRET=RECAPTCHA_TEST_SECRET)
class RegisterTest(APITestCase):
    def test_register(self):
        """
        Registration should be possible
        """
        response = self.client.post(
            reverse('account:register'), {
                'username': "testUser",
                'email': "testUser@example.invalid",
                'password': "password$123",
                'captcha': "captchaResult"  # Captcha checks never fail with test secret
            })

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(get_user_model().objects.filter(username="testUser").exists())
        
    def test_register_same_nick(self):
        """
        Every username only once
        """
        get_user_model().objects.create_user(username="user", email="user@example.invalid", password="secret")

        response = self.client.post(
            reverse('account:register'), {
                'username': "useR",  # Case insensitive
                'email': "userAlt@example.invalid",
                'password': "password123",
                'captcha': "captchaResult"  # Captcha checks never fail with test secret
            })

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


@override_settings(RECAPTCHA_SECRET=RECAPTCHA_TEST_SECRET)
class RecoverTest(APITestCase):
    def setUp(self):
        self.user = get_user_model().objects.create(username="user", email="user@example.com", password="secret")
        self.user1 = get_user_model().objects.create(username="user1", email="user1@example.com", password="secret")
        self.user2 = get_user_model().objects.create(username="user2", email="user1@example.com", password="secret")

    def test_get_username_one(self):
        """
        Get the username, when only one username has the specific email address
        """
        mail.outbox = []

        response = self.client.post(
            reverse('account:recover'), {
                'email': self.user.email,
                'captcha': "captchaResult"
            })

        join_all_threads()
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(len(mail.outbox), 1)

    def test_get_username_multiple(self):
        """
        Get the username, when multiple usernames have the specific address
        """
        mail.outbox = []

        response = self.client.post(
            reverse('account:recover'), {
                'email': self.user1.email,
                'captcha': "captchaResult"
            })

        join_all_threads()
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(len(mail.outbox), 1)

    def test_get_username_none(self):
        """
        Try with an email with no assigned usernames.
        Status code should still be 201, but no email should be send.
        """
        mail.outbox = []

        response = self.client.post(
            reverse('account:recover'), {
                'email': "nobody@example.invalid",
                'captcha': "captchaResult"
            })

        join_all_threads()
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(len(mail.outbox), 0)

    def test_reset_password(self):
        """
        Reset the password of a user
        """
        mail.outbox = []

        response1 = self.client.post(
            reverse('account:recover'), {
                'email': self.user1.email,
                'username': self.user1.username,
                'captcha': "captchaResult"
            })

        join_all_threads()
        self.assertEqual(response1.status_code, status.HTTP_201_CREATED)
        self.assertEqual(len(mail.outbox), 1)

        transaction = response1.data['transaction']
        resetObj = ResetPassword.objects.get(transaction=transaction)

        self.assertIsNotNone(transaction)
        self.assertIn(resetObj.token, mail.outbox[0].body)
        self.assertEqual(resetObj.user, self.user1)

        new_password = "highQualw39Qdjf@♣asdk34kasdUI$E"
        response2 = self.client.post(
            reverse('account:reset-password'), {
                'transaction': transaction,
                'token': resetObj.token,
                'new_password': new_password,
                'captcha': "captchaResult"
            })

        self.assertEqual(response2.status_code, status.HTTP_201_CREATED)
        self.assertIsNotNone(authenticate(username=self.user1.username, password=new_password))  # Check if new password is considered valid
        with self.assertRaises(ResetPassword.DoesNotExist):
            ResetPassword.objects.get(pk=resetObj.pk)

    def test_reset_password_invalid_email(self):
        """
        Reset the password with invalid user data
        """
        mail.outbox = []

        response = self.client.post(
            reverse('account:recover'), {
                'email': "nobody@example.invalid",
                'username': self.user1.username,
                'captcha': "captchaResult"
            })

        join_all_threads()
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(len(mail.outbox), 0)
        self.assertIsNotNone(response.data['transaction'])

    def test_reset_password_invalid_email(self):
        """
        Reset the password with invalid user data
        """
        mail.outbox = []

        response = self.client.post(
            reverse('account:recover'), {
                'email': self.user1.email,
                'username': "thisIsNotMyUserName",
                'captcha': "captchaResult"
            })

        join_all_threads()
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(len(mail.outbox), 0)
        self.assertIsNotNone(response.data['transaction'])

    def test_reset_invalid_data(self):
        new_password = "highQualw39Qdjf@♣asdk34kasdUI$E"
        response = self.client.post(
            reverse('account:reset-password'), {
                'transaction': uuid.uuid4(),
                'token': token_urlsafe(50),
                'new_password': new_password,
                'captcha': "captchaResult"
            })

        self.assertEqual(response.status_code, 404)

    def test_reset_invalid_token(self):
        resetObj = ResetPassword.objects.create(user=self.user)
        new_password = "highQualw39Qdjf@♣asdk34kasdUI$E"
        response = self.client.post(
            reverse('account:reset-password'), {
                'transaction': resetObj.transaction,
                'token': token_urlsafe(50),
                'new_password': new_password,
                'captcha': "captchaResult"
            })

        self.assertEqual(response.status_code, 404)
        self.assertIsNone(authenticate(username=self.user.username, password=new_password))
        # Reset object should still exist
        ResetPassword.objects.get(pk=resetObj.pk)
