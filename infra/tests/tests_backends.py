'''Unit tests for infra backends.'''
from unittest.mock import patch, Mock

from django.core.mail import EmailMessage
from django.test import TestCase

from infra.exceptions import InternalServerError, BadRequest
from infra.backends import SOAPEmailBackend


class TestSOAPEmailBackend(TestCase):
    '''Unit tests for SOAPEmailBackend.'''
    @classmethod
    def setUpTestData(cls):
        cls.backend = SOAPEmailBackend()

    def test_recipient_is_email(self):
        '''Should return True is recipient is Email.'''

        res = self.backend.recipient_is_email('abc@def.gh')

        self.assertTrue(res)

    def test_recipient_is_not_email(self):
        '''Should return False is recipient is not Email.'''

        res = self.backend.recipient_is_email('abcdef')

        self.assertFalse(res)

    def test_format_recipient_fail(self):
        '''Should raise exception if recipient is not an email address.'''
        recipients = ['abcdef.gh']

        with self.assertRaisesMessage(BadRequest, '邮箱地址无效'):
            self.backend.format_recipients(recipients)

    def test_format_single_recipient(self):
        '''Should format single recipient correctly.'''

        recipients = ['abc@def.gh']

        res = self.backend.format_recipients(recipients)

        self.assertEqual(res, f'||||{recipients[0]}')

    def test_format_multiple_recipients(self):
        '''Should format multiple recipients correctly.'''
        recipients = ['abc@def.gh', 'abccc@ggg.com']

        res = self.backend.format_recipients(recipients)

        self.assertEqual(res, f'||||{recipients[0]}^@^||||{recipients[1]}')

    @patch('infra.backends.InMemoryCache', Mock())
    @patch('infra.backends.Transport', Mock())
    @patch('infra.backends.prod_logger')
    @patch('infra.backends.Client')
    def test_send_messages_wsdl_fail(self, mocked_client, mocked_logger):
        '''Should raise exception if failed to create SOAP client.'''

        mocked_client.side_effect = Exception()

        with self.assertRaisesMessage(InternalServerError, '邮件服务暂时不可用'):
            self.backend.send_messages([])

        mocked_logger.warning.assert_called()

    @patch('infra.backends.InMemoryCache', Mock())
    @patch('infra.backends.Transport', Mock())
    @patch('infra.backends.prod_logger')
    @patch('infra.backends.Client')
    def test_send_messages_send_fail(self, mocked_client, mocked_logger):
        '''Should raise exception if failed to send email.'''

        mocked_client.return_value = mocked_client
        mocked_client.service.saveEmailInfo.side_effect = Exception('Unknown')
        email_message = EmailMessage('a', 'b', 'from', ['c@d.com', 'a@b.com'])
        with self.assertRaisesMessage(InternalServerError, '邮件发送失败'):
            self.backend.send_messages([email_message])

        msg = '邮件发送失败, 失败原因: Unknown'
        mocked_logger.warning.assert_called_with(msg)

    @patch('infra.backends.InMemoryCache', Mock())
    @patch('infra.backends.Transport', Mock())
    @patch('infra.backends.prod_logger')
    @patch('infra.backends.Client')
    def test_send_messages_send_succeed(self, mocked_client, mocked_logger):
        '''Should send email via SOAP client.'''

        mocked_client.return_value = mocked_client
        mocked_client.service.saveEmailInfo.return_value = (
            '{"result":true,"msg":"success","msg_id":"123"}'
        )
        email_message = EmailMessage('a', 'b', 'from', ['a@c.com', 'a@b.com'])
        self.backend.send_messages([email_message])

        msg = "邮件发送成功, 收件人: ['a@c.com', 'a@b.com'], 标题: a, 消息ID: 123"
        mocked_logger.info.assert_called_with(msg)

    @patch('infra.backends.InMemoryCache', Mock())
    @patch('infra.backends.Transport', Mock())
    @patch('infra.backends.prod_logger')
    @patch('infra.backends.Client')
    def test_send_messages_service_fail(self, mocked_client, mocked_logger):
        '''Should send email via SOAP client.'''

        mocked_client.return_value = mocked_client
        mocked_client.service.saveEmailInfo.return_value = (
            '{"result":false,"msg":"failed reason","msg_id":"123"}'
        )
        email_message = EmailMessage('a', 'b', 'from', ['aa@c.com', 'a@b.com'])
        with self.assertRaisesMessage(InternalServerError, '邮件发送失败'):
            self.backend.send_messages([email_message])

        msg = '邮件发送失败, 失败原因: failed reason'
        mocked_logger.warning.assert_called_with(msg)
