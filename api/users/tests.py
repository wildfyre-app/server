import django
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser
from django.test import TestCase
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIRequestFactory, APITestCase, force_authenticate

from .models import *
from .views import *


class ProfileTest(TestCase):
    def setUp(self):
        # We need the test factory for all tests
        self.factory = APIRequestFactory()
        # Test User
        self.user1 = get_user_model().objects.create_user(
            username='user1', email='user1@example.invalid', password='secret')

        self.user2_profile = get_user_model().objects.create_user(
            username='user2', email='user2@example.invalid', password='secret')

        self.profile2 = Profile.objects.create(
            user=self.user2_profile, bio="Hello I'm a test user!")

    def test_not_authenticated(self):
        """
        Status code 401: Unauthorized should be raised
        """
        request = self.factory.get(reverse('users:profile'))
        request.user = AnonymousUser()
        response = ProfileView.as_view()(request)

        self.assertEqual(response.status_code, 401)

class UserProfileTest(TestCase):
    def setUp(self):
        # We need the test factory for all tests
        self.factory = APIRequestFactory()
        # Test User
        self.user1 = get_user_model().objects.create_user(
            username='user1', email='user1@example.invalid', password='secret')

        self.user2 = get_user_model().objects.create_user(
            username='user2', email='user2@example.invalid', password='secret')

        self.profile1 = Profile.objects.create(
            user=self.user1, bio="Hello I'm a test user!")

    def test_view(self):
        """
        Users should be able to view
        """
        request = self.factory.get(reverse(
            'users:profile',
            kwargs={'user': self.user1.pk}))
        response = UserProfileView.as_view()(request, user=self.user1.pk)

        self.assertEqual(response.status_code, 200)

    def test_patch(self):
        """
        Other users entry shouldn't be editable
        Response with 405: Method Not Allowed
        """
        request = self.factory.patch(
            reverse(
                'users:profile',
                kwargs={'user': self.user1.pk}),
            {'bio': "Hi ther!"})
        force_authenticate(request, user=self.user2)
        response = UserProfileView.as_view()(request, user=self.user1.pk)

        self.assertEqual(response.status_code, 405)


class ProfileAutoCreateTest(APITestCase):
    def setUp(self):
        # Test User
        self.user1 = get_user_model().objects.create_user(
            username='user1', email='user1@example.invalid', password='secret')

        self.user2 = get_user_model().objects.create_user(
            username='user2', email='user2@example.invalid', password='secret')

    def test_own(self):
        """
        Create profile when accessing ProfileView
        """
        self.client.force_authenticate(user=self.user1)
        response = self.client.get(reverse('users:profile'))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(Profile.objects.all().filter(user=self.user1).exists())

    def test_other(self):
        
        """
        Create profile when accessing UserProfileView
        """
        self.client.force_authenticate(user=self.user1)
        response = self.client.get(reverse('users:profile', kwargs={'user': self.user2.pk}))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(Profile.objects.all().filter(user=self.user2).exists())

    def test_own_by_id(self):
        """
        Create profile when accessing self in UserProfileView
        """
        self.client.force_authenticate(user=self.user1)
        response = self.client.get(reverse('users:profile', kwargs={'user': self.user1.pk}))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(Profile.objects.all().filter(user=self.user1).exists())
