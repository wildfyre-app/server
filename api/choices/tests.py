import django
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from . import BAN_REASON_CHOICES

class ReasonTest(APITestCase):
    def test_ban_reason(self):
        """
        Retrive the reasons for a ban.
        """
        response = self.client.get(reverse('choices:ban-reasons'))

        data = []
        for k in BAN_REASON_CHOICES:
            data.append({'key': k[0], 'value': k[1]})

        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, data)
