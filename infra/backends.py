'''Backends provided by infra module.'''
import json
import re

from django.conf import settings
from django.core.mail.backends.base import BaseEmailBackend
from zeep import Client
from zeep.cache import InMemoryCache
from zeep.transports import Transport

from infra.utils import prod_logger


class SOAPEmailBackend(BaseEmailBackend):
    '''Provide Email service via web service.'''
    def send_messages(self, email_messages):
        transport = Transport(cache=InMemoryCache())
        client = Client(
            f'{settings.SOAP_BASE_URL}/EmailService?wsdl',
            transport=transport
        )

        # TODO(youchen): Verity field names
        default_payload = {
            # Auth-related
            'tp_name': settings.SOAP_AUTH_TP_NAME,
            'sys_id': settings.SOAP_AUTH_SYS_ID,
            'module_id': settings.SOAP_AUTH_MODULE_ID,
            # TODO(youchen): Encrypt with sha
            'secret_key': settings.SOAP_AUTH_SECRET_KEY,
            'interface_method': settings.SOAP_AUTH_INTERFACE_METHOD,

            # Business-related
            'receive_person_info': '',  # Required
            'email_title': '',  # Required
            'email_info': '',  # Required
            'send_priority': '3',  # Send now
            'templet_id': '0',
            'receipt_id': '0',
            'send_sys_id': '1',
        }
        for message in email_messages:
            payload = default_payload.copy()
            payload['receive_person_info'] = self.format_recipients(message.to)
            payload['email_title'] = message.subject
            payload['email_info'] = message.body
            email_info = json.dumps(payload)
            try:
                client.service.saveEmailInfo(email_info)
            except Exception as err:  # pylint: disable=broad-except
                msg = f'邮件发送失败, 失败原因: {err.message}'
                prod_logger.warning(msg)
                raise
            else:
                msg = (
                    f'邮件发送成功, 收件人: {message.to}, '
                    f'标题: {message.subject}'
                )
                prod_logger.info(msg)

    @staticmethod
    def recipient_is_email(recipient):
        '''Return True if recipient is in format 'x@y.z'.'''
        return re.match(r'^.+?@.+?\..+?$', recipient) is not None


    def format_recipients(self, recipients):
        '''Format recipients to string.

        Recipient is formatted into "Name|ID|DepartmentID|DepartmentName|Email",
        fields are optional but vertical bar is required, multiple recipients
        are separated by "^@^".
        '''
        res = ''
        for recipient in recipients:
            if res != '':
                res += '^@^'
            if self.recipient_is_email(recipient):
                res += f'||||{recipient}'
            else:
                res += f'|{recipient}|||'
        return res
        