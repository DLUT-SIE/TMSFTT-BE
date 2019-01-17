'''Unit tests for auth serializers.'''
from django.test import TestCase

import infra.serializers as serializers
import infra.models as models


class TestNotificationSerializer(TestCase):
    '''Unit tests for serializer of notification.'''
    def test_fields_equal(self):
        '''Serializer should return fields of notification correctly.'''
        notification = models.Notification()
        expected_keys = {'id', 'time', 'sender', 'recipient',
                         'content', 'read_time'}
        keys = set(serializers.NotificationSerializer(notification).
                   data.keys())
        self.assertEqual(keys, expected_keys)
