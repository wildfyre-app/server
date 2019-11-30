from datetime import timedelta

import django
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.utils import timezone

from rest_framework import status
from rest_framework.test import APITestCase

from .models import Ban, Warn
from .views import BanView


class BanTest(APITestCase):
    def setUp(self):
        # Users
        self.goodUser = get_user_model().objects.create_user(
            username='goodGuy', password='secret')
        self.evilUser = get_user_model().objects.create_user(
            username='evil', password='secret')
        self.unbannedUser = get_user_model().objects.create_user(
            username='unbanned', password='secret')
        self.expiredUser = get_user_model().objects.create_user(
            username='expired', password='secret')
        self.multi_bans = get_user_model().objects.create_user(
            username='multi', password='secret')

        # Ban
        Ban.objects.create(user=self.evilUser, ban_all=True)
        Ban.objects.create(user=self.unbannedUser, ban_all=True, unbanned=True)
        Ban.objects.create(user=self.expiredUser, ban_all=True, expiry=timezone.now() - timedelta(days=10))
        Ban.objects.create(user=self.multi_bans, ban_post=True)
        Ban.objects.create(user=self.multi_bans, ban_comment=True)

    def test_not_banned(self):
        """
        Users without a ban should get an empty list
        The same for unbanned users and when the ban expired
        """
        not_banned = [self.goodUser, self.unbannedUser, self.expiredUser,]

        for user in not_banned:
            self.client.force_authenticate(user=user)
            response = self.client.get(reverse('bans:bans'))

            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(response.data['results'], [])

    def test_banned(self):
        """
        Users who are currently banned should see that ban
        """
        self.client.force_authenticate(user=self.evilUser)
        response = self.client.get(reverse('bans:bans'))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        
        ban = response.data['results'][0]
        self.assertTrue(ban['ban_all'])
        items = ['timestamp', 'reason', 'comment', 'expiry', 'ban_all', 'ban_comment', 'ban_flag',]
        for item in items:
            self.assertIn(item, ban)

    def test_multiple_bans(self):
        """
        Users with multiple bans should see all of them
        """
        self.client.force_authenticate(user=self.multi_bans)
        response = self.client.get(reverse('bans:bans'))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreater(len(response.data['results']), 1)

        for ban in response.data['results']:
            self.assertFalse(ban['ban_all'])
            items = ['timestamp', 'reason', 'comment', 'expiry', 'ban_all', 'ban_comment', 'ban_flag',]
            for item in items:
                self.assertIn(item, ban)

    def test_ban_on_profile(self):
        """
        The banned value on the users profile should return true
        """
        self.client.force_authenticate(user=self.multi_bans)
        response = self.client.get(reverse('users:profile'))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['banned'])
