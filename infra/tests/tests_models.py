'''Unit tests for infra models.'''
from django.test import TestCase
from django.utils.timezone import now
from django.utils.text import format_lazy as _f


from infra.models import OperationLog, Notification


class TestOperationLog(TestCase):
    '''Unit tests for model OperationLog.'''
    def test_str(self):
        '''Should render string correctly.'''
        time = now()
        requester_id = 123
        method = 1
        url = 'http://www.foo.bar'

        log = OperationLog(
            time=time, method=method, url=url, requester_id=requester_id)

        self.assertEqual(str(log), '{}({} {} {})'.format(
            time, requester_id, method, url))


class TestNotification(TestCase):
    '''Unit tests for model Notification.'''
    def test_str(self):
        '''Should render string correctly.'''
        time = now()
        sender_id = 123
        recipient_id = 456
        test_cases = (
            # Unread
            ((time, None), _f('由{}于{}发送给{}的通知({})',
                              sender_id, time, recipient_id, '未读')),
            # Read
            ((time, time), _f('由{}于{}发送给{}的通知({})',
                              sender_id, time, recipient_id, '已读')),
        )
        for args, expected_str in test_cases:
            note = Notification(
                time=args[0], read_time=args[1],
                sender_id=sender_id, recipient_id=recipient_id)
            self.assertEqual(str(note), str(expected_str))
