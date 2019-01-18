'''Unit tests for infra models.'''
from unittest.mock import patch

from django.test import TestCase
from django.utils.timezone import now
from django.utils.text import format_lazy as _f


from infra.models import Notification


class TestNotification(TestCase):
    '''Unit tests for model Notification.'''
    @patch('infra.models.Notification.sender')
    @patch('infra.models.Notification.recipient')
    def test_str(self, mocked_recipient, mocked_sender):
        '''Should render string correctly.'''
        time = now()
        recipient = 'recipient'
        sender = 'sender'
        mocked_recipient.__str__.return_value = recipient
        mocked_sender.__str__.return_value = sender
        test_cases = (
            # Unread
            ((time, None), _f('由{}于{}发送给{}的通知({})',
                              sender, time, recipient, '未读')),
            # Read
            ((time, time), _f('由{}于{}发送给{}的通知({})',
                              sender, time, recipient, '已读')),
        )
        for args, expected_str in test_cases:
            note = Notification(time=args[0], read_time=args[1])
            self.assertEqual(str(note), str(expected_str))
