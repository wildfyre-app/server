import django
from django.urls import reverse
from django.test import TestCase
from rest_framework.test import APIRequestFactory, force_authenticate
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser

from .views import *
from .models import *

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

    def test_create_profile(self):
        """
        Create Profile for user via post.
        Should respond with status code 201: Created
        """
        request = self.factory.post(reverse('users:profile'), {'bio': "Hi this is my bio"})
        force_authenticate(request, self.user1)
        response = ProfileView.as_view()(request)

        self.assertEqual(response.status_code, 201)

    def test_create_secound_profile(self):
        """
        Users may only have one profile
        Should respond with status code 400: Bad Request
        """
        request = self.factory.post(reverse('users:profile'), {'bio': "Hi this is my bio"})
        force_authenticate(request, self.user2_profile)
        response = ProfileView.as_view()(request)

        self.assertEqual(response.status_code, 400)

    def test_send_additional_parameters(self):
        """
        Sending additional parameters should have no effect.
        Trying here with id and user as these must not be used from the request
        """
        bio = "test_send_additional_parameters"  # Used to identify object
        request = self.factory.post(
            reverse('users:profile'),
            {'bio': bio, 'user': self.user2_profile, 'id': -1})
        force_authenticate(request, self.user1)
        response = ProfileView.as_view()(request)

        profile1 = Profile.objects.get(bio=bio)

        # Object should still be created ...
        self.assertEqual(response.status_code, 201)
        # ... but unnessesary parms should be ignored
        self.assertEqual(profile1.user, self.user1)
        self.assertNotEqual(profile1.id, -1)

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