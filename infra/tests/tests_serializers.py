'''Unit tests for auth serializers.'''
from django.contrib.auth import get_user_model
from django.test import TestCase

import infra.serializers as serializers
import infra.models as models


User = get_user_model()


class TestUserSerializer(TestCase):
    '''Unit tests for serializer of User.'''
    def test_fields_equal(self):
        '''Serializer should return fields of User correctly.'''
        user = User()
        expected_keys = {
            'id', 'last_login', 'first_name', 'last_name', 'email',
            'is_active', 'date_joined'}

        keys = set(serializers.UserSerializer(user).data.keys())
        self.assertEqual(keys, expected_keys)


class TestOperationLogSerializer(TestCase):
    '''Unit tests for serializer of operationlog.'''
    def test_fields_equal(self):
        '''Serializer should return fields of operationlog correctly.'''
        department = models.OperationLog()
        expected_keys = {'id', 'time', 'remote_ip', 'requester', 'method',
                         'url', 'referrer', 'user_agent'}
        keys = set(serializers.OperationLogSerializer(department).data.keys())
        self.assertEqual(keys, expected_keys)


class TestNotificationSerializer(TestCase):
    '''Unit tests for serializer of notification.'''
    def test_fields_equal(self):
        '''Serializer should return fields of notification correctly.'''
        profile = models.Notification()
        expected_keys = {'id', 'time', 'sender', 'recipient',
                         'content', 'read_time'}
        keys = set(serializers.NotificationSerializer(profile).data.keys())
        self.assertEqual(keys, expected_keys)
