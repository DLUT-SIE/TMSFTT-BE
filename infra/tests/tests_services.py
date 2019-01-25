'''Unit tests for infra services.'''
from unittest.mock import patch, call

from django.test import TestCase

from infra.services import NotificationService


class TestNotificationService(TestCase):
    '''Unit tests for NotificationService.'''
    @classmethod
    def setUpTestData(cls):
        cls.service = NotificationService

    @patch('infra.services.now')
    @patch('infra.services.Notification.objects')
    def test_mark_user_notifications_as_read(self, mocked_objects, mocked_now):
        '''Should set read_time of notifications.'''
        now = '2019-01-01'
        mocked_now.return_value = now
        mocked_objects.filter.return_value = mocked_objects
        user_pk = 1

        self.service.mark_user_notifications_as_read(user_pk)

        calls = [call(recipient__pk=user_pk), call(read_time=None)]
        mocked_objects.filter.assert_has_calls(calls)
        mocked_objects.update.assert_called_with(read_time=now)

    @patch('infra.services.Notification.objects')
    def test_delete_user_notifications(self, mocked_objects):
        '''Should delete notifications.'''
        mocked_objects.filter.return_value = mocked_objects
        user_pk = 1

        self.service.delete_user_notifications(user_pk)

        mocked_objects.filter.assert_called_with(recipient__pk=user_pk)
        mocked_objects.delete.assert_called()
