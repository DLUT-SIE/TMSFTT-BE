'''Unit tests for auth views.'''
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.urls import reverse
from django.utils.timezone import now
from model_mommy import mommy
from rest_framework import status
from rest_framework.test import APITestCase

import infra.models
from auth.utils import assign_perm


class TestNotificationViewSet(APITestCase):
    '''Unit tests for Notification view.'''
    @classmethod
    def setUpTestData(cls):
        cls.user = mommy.make(get_user_model())
        assign_perm('infra.view_notification', cls.user)

    def test_list_notification(self):
        '''notification list should be accessed by GET request.'''
        url = reverse('notification-list')

        self.client.force_authenticate(self.user)
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_notification(self):
        '''notification should be accessed by GET request.'''
        user = self.user
        notification = mommy.make(infra.models.Notification, recipient=user)
        assign_perm('infra.view_notification', user, notification)
        url = reverse('notification-detail', args=(notification.pk,))

        self.client.force_authenticate(user)
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('id', response.data)
        self.assertEqual(response.data['id'], notification.id)

    def test_list_read_notifications(self):
        '''should return notifications which are already read.'''
        user = self.user
        for index in range(10):
            notification = mommy.make(
                infra.models.Notification,
                read_time=now() if index % 4 == 0 else None,
                recipient=user)
            assign_perm('infra.view_notification', user, notification)
        url = reverse('notification-read')

        self.client.force_authenticate(user)
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 3)

    def test_list_unread_notifications(self):
        '''should return notifications which are already read.'''
        user = self.user
        for index in range(10):
            notification = mommy.make(
                infra.models.Notification,
                read_time=now() if index % 4 == 0 else None,
                recipient=user)
            assign_perm('view_notification', user, notification)
        url = reverse('notification-unread')

        self.client.force_authenticate(user)
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 7)

    @patch('infra.views.NotificationViewSet.paginate_queryset')
    def test_return_full_if_no_pagination(self, mocked_paginate):
        '''should return full page if no pagination is required.'''
        url = reverse('notification-unread')
        mocked_paginate.return_value = None

        self.client.force_authenticate(self.user)
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)


class TestNotificationActionViewSet(APITestCase):
    '''Unit tests for NotificationActionViewSet.'''

    @patch('infra.views.NotificationService')
    def test_mark_all_as_read(self, mocked_service):
        '''Should call mark_user_notifications_as_read.'''
        user = mommy.make(get_user_model())
        url = reverse('notification-actions-read-all')
        mocked_service.mark_user_notifications_as_read.return_value = 3

        self.client.force_authenticate(user)
        response = self.client.post(url)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('count', response.data)
        mocked_service.mark_user_notifications_as_read.assert_called_with(user)

    @patch('infra.views.NotificationService')
    def test_delete_all_notifications(self, mocked_service):
        '''Should call delete_user_notifications.'''
        user = mommy.make(get_user_model())
        url = reverse('notification-actions-delete-all')
        mocked_service.delete_user_notifications.return_value = 3

        self.client.force_authenticate(user)
        response = self.client.post(url)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('count', response.data)
        mocked_service.delete_user_notifications.assert_called_with(user)
