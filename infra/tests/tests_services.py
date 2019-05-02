'''Unit tests for infra services.'''
from unittest.mock import patch, call, Mock

from django.test import TestCase
from django.contrib.auth import get_user_model
from model_mommy import mommy

from infra.services import NotificationService
from infra.models import Notification


User = get_user_model()


class TestNotificationService(TestCase):
    '''Unit tests for NotificationService.'''
    @classmethod
    def setUpTestData(cls):
        User.objects.get_or_create(
            username='notification-robot', defaults={'first_name': '系统通知'}
        )
        cls.service = NotificationService

    @patch('infra.services.now')
    @patch('infra.services.Notification.objects')
    def test_mark_user_notifications_as_read(self, mocked_objects, mocked_now):
        '''Should set read_time of notifications.'''
        now = '2019-01-01'
        mocked_now.return_value = now
        mocked_objects.filter.return_value = mocked_objects
        user = Mock()

        self.service.mark_user_notifications_as_read(user)

        calls = [call(recipient=user), call(read_time=None)]
        mocked_objects.filter.assert_has_calls(calls)
        mocked_objects.update.assert_called_with(read_time=now)

    @patch('infra.services.Notification.objects')
    def test_delete_user_notifications(self, mocked_objects):
        '''Should delete notifications.'''
        mocked_objects.filter.return_value = mocked_objects
        user = Mock()

        self.service.delete_user_notifications(user)

        mocked_objects.filter.assert_called_with(recipient=user)
        mocked_objects.delete.assert_called()

    def test_send_system_notification_user_instance(self):
        '''Should send notification for user instance.'''
        user = mommy.make(User)
        content = 'Hello World!'

        self.service.send_system_notification(user, content)

        notification = Notification.objects.filter(recipient=user)
        self.assertEqual(len(notification), 1)
        notification = notification[0]
        self.assertEqual(notification.recipient.id, user.id)
        self.assertEqual(notification.content, content)

    def test_send_system_notification_user_id(self):
        '''Should send notification for user id.'''
        user = mommy.make(User)
        content = 'Hello World!'

        self.service.send_system_notification(user.id, content)

        notification = Notification.objects.filter(recipient=user)
        self.assertEqual(len(notification), 1)
        notification = notification[0]
        self.assertEqual(notification.recipient.id, user.id)
        self.assertEqual(notification.content, content)

    def test_send_system_notification_raise_exception(self):
        '''Should raise exception for not supported recipient.'''
        user = mommy.make(User)
        content = 'Hello World!'

        with self.assertRaises(ValueError):
            self.service.send_system_notification(user.username, content)

        count = Notification.objects.filter(recipient=user).count()
        self.assertEqual(count, 0)
