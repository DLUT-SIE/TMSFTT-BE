'''Unit tests for auth views.'''
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.urls import reverse
from django.utils.timezone import now
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
        user = mommy.make(get_user_model())
        notification = mommy.make(infra.models.Notification, recipient=user)
        url = reverse('notification-detail', args=(notification.pk,))

        self.client.force_authenticate(user)
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('id', response.data)
        self.assertEqual(response.data['id'], notification.id)

    def test_list_read_notifications(self):
        '''should return notifications which are already read.'''
        user = mommy.make(get_user_model())
        for index in range(10):
            mommy.make(infra.models.Notification,
                       read_time=now() if index % 4 == 0 else None,
                       recipient=user)
        url = reverse('notification-read')

        self.client.force_authenticate(user)
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 3)

    def test_list_unread_notifications(self):
        '''should return notifications which are already read.'''
        user = mommy.make(get_user_model())
        for index in range(10):
            mommy.make(infra.models.Notification,
                       read_time=now() if index % 4 == 0 else None,
                       recipient=user)
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

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)


class TestNotificationTaskViewSet(APITestCase):
    '''Unit tests for NotificationTask.'''

    @patch('infra.views.NotificationService')
    def test_mark_all_notifications_as_read(self, mocked_service):
        '''Should call mark_user_notifications_as_read.'''
        user = mommy.make(get_user_model())
        url = reverse('notification-user-tasks-mark-all-notifications-as-read',
                      kwargs={'user_pk': user.pk})

        self.client.force_authenticate(user)
        response = self.client.post(url)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        mocked_service.mark_user_notifications_as_read.assert_called_with(
            user.pk)

    @patch('infra.views.NotificationService')
    def test_delete_all_notifications(self, mocked_service):
        '''Should call delete_user_notifications.'''
        user = mommy.make(get_user_model())
        url = reverse('notification-user-tasks-delete-all-notifications',
                      kwargs={'user_pk': user.pk})

        self.client.force_authenticate(user)
        response = self.client.post(url)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        mocked_service.delete_user_notifications.assert_called_with(user.pk)
