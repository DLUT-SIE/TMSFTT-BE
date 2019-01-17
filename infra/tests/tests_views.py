'''Unit tests for auth views.'''
from django.urls import reverse
from model_mommy import mommy
from rest_framework import status
from rest_framework.test import APITestCase

import infra.models


class TestNotificationViewSet(APITestCase):
    '''Unit tests for Notification view.'''
    def test_list_notification(self):
        '''notification list should be accessed by GET request.'''
        url = reverse('notification-list')

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_notification(self):
        '''notification should be accessed by GET request.'''
        notification = mommy.make(infra.models.Notification)
        url = reverse('notification-detail', args=(notification.pk,))

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('id', response.data)
        self.assertEqual(response.data['id'], notification.id)
