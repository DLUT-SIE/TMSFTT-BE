'''Unit tests for infra models.'''
from unittest.mock import Mock
from django.test import TestCase
from django.utils.timezone import now
from django.contrib.auth import get_user_model
from model_mommy import mommy


from infra.models import OperationLog, Notification

User = get_user_model()


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

    def test_from_response(self):
        '''Should create instance from request and response.'''
        request = Mock()
        path_info = Mock()
        request.user = mommy.make(User)
        request.get_full_path_info.return_value = path_info
        request.method = 'POST'
        request.META = {
            'REMOTE_ADDR': '127.0.0.1',
            'HTTP_REFERER': 'referer',
            'HTTP_USER_AGENT': 'user-agent',
        }
        response = Mock()
        response.status_code = 400

        log = OperationLog.from_response(request, response)

        self.assertEqual(log.remote_ip, request.META['REMOTE_ADDR'])
        self.assertIs(log.requester, request.user)
        self.assertEqual(log.method,
                         OperationLog.HTTP_METHODS_DICT[request.method])
        self.assertEqual(log.url, path_info)
        self.assertEqual(log.referrer, request.META['HTTP_REFERER'])
        self.assertEqual(log.user_agent, request.META['HTTP_USER_AGENT'])
        self.assertEqual(log.status_code, response.status_code)


class TestNotification(TestCase):
    '''Unit tests for model Notification.'''
    def test_str(self):
        '''Should render string correctly.'''
        time = now()
        sender_id = 123
        recipient_id = 456
        test_cases = (
            # Unread
            ((time, None), '由{}于{}发送给{}的通知({})'.format(
                sender_id, time, recipient_id, '未读')),
            # Read
            ((time, time), '由{}于{}发送给{}的通知({})'.format(
                sender_id, time, recipient_id, '已读')),
        )
        for args, expected_str in test_cases:
            note = Notification(
                time=args[0], read_time=args[1],
                sender_id=sender_id, recipient_id=recipient_id)
            self.assertEqual(str(note), str(expected_str))
