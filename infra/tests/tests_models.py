from unittest.mock import patch

from django.test import TestCase
from django.utils.timezone import now
from django.utils.translation import gettext_lazy as _


from infra.models import OperationLog, Notification


class TestOperationLog(TestCase):
    @patch('infra.models.OperationLog.requester')
    def test_str(self, mocked_requester):
        time = now()
        requester = 'requester'
        method = 1
        url = 'http://www.foo.bar'
        mocked_requester.__str__.return_value = requester

        log = OperationLog(
            time=time, method=method, url=url)

        self.assertEqual(str(log), '{}({} {} {})'.format(
            time, requester, method, url))


class TestNotification(TestCase):
    @patch('infra.models.Notification.sender')
    @patch('infra.models.Notification.recipient')
    def test_str(self, mocked_recipient, mocked_sender):
        time = now()
        recipient = 'recipient'
        sender = 'sender'
        mocked_recipient.__str__.return_value = recipient
        mocked_sender.__str__.return_value = sender
        test_cases = (
            # Unread
            ((time, None), _('由{}于{}发送给{}的通知({})').format(
                sender, time, recipient, '未读')),
            # Read
            ((time, time), _('由{}于{}发送给{}的通知({})').format(
                sender, time, recipient, '已读')),
        )
        for args, expected_str in test_cases:
            note = Notification(time=args[0], read_time=args[1])
            self.assertEqual(str(note), expected_str)
