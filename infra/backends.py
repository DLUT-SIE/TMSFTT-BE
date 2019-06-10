'''Backends provided by infra module.'''
import base64
import hashlib
import json
import re

from django.conf import settings
from django.core.mail.backends.base import BaseEmailBackend
from zeep import Client
from zeep.cache import InMemoryCache
from zeep.transports import Transport

from infra.exceptions import InternalServerError, BadRequest
from infra.utils import prod_logger


class SOAPEmailBackend(BaseEmailBackend):
    '''Provide Email service via web service.'''
    def send_messages(self, email_messages):
        transport = Transport(cache=InMemoryCache())
        try:
            client = Client(
                f'{settings.SOAP_BASE_URL}/EmailService?wsdl',
                transport=transport
            )
        except Exception:
            prod_logger.warning('获取WSDL失败，邮件服务暂时不可用')
            raise InternalServerError('邮件服务暂时不可用')

        # According to the protocol, we need encrypt our secret_key with
        # SHA-1 and encode with base64
        sha1 = hashlib.sha1()
        sha1.update(settings.SOAP_AUTH_SECRET_KEY.encode())
        secret_key = base64.b64encode(sha1.digest())

        default_payload = {
            # Auth-related
            'tp_name': settings.SOAP_AUTH_TP_NAME,
            'sys_id': settings.SOAP_AUTH_SYS_ID,
            'module_id': settings.SOAP_AUTH_MODULE_ID,
            'secret_key': secret_key.decode(),
            'interface_method': 'email',

            # Business-related
            # NOTE: recieve_person_info is the correct parameter name,
            # I know it's a typo but it's required by the interface
            'recieve_person_info': '',  # Required
            # NOTE: Again, emial_title is the correct parameter name
            'emial_title': '',  # Required
            'email_info': '',  # Required
            'send_priority': '3',  # Send now
            'templet_id': '0',
            'receipt_id': '0',
            'send_sys_id': '1',
        }
        for message in email_messages:
            payload = default_payload.copy()
            payload['recieve_person_info'] = self.format_recipients(message.to)
            payload['emial_title'] = message.subject
            payload['email_info'] = message.body
            email_info = json.dumps(payload)
            try:
                resp = client.service.saveEmailInfo(email_info)
                resp = json.loads(resp)
                if resp['result'] is False:
                    raise Exception(resp['msg'])
            except Exception as err:
                msg = f'邮件发送失败, 失败原因: {err}'
                prod_logger.warning(msg)
                raise InternalServerError('邮件发送失败')
            else:
                msg = (
                    f'邮件发送成功, 收件人: {message.to}, '
                    f'标题: {message.subject}, '
                    f'消息ID: {resp["msg_id"]}'
                )
                prod_logger.info(msg)

    @staticmethod
    def recipient_is_email(recipient):
        '''Return True if recipient is in format 'x@y.z'.'''
        return re.match(r'^.+?@.+?\..+?$', recipient) is not None

    def format_recipients(self, recipients):
        '''Format recipients to string.

        Recipient is formatted into
        "Name|ID|DepartmentID|DepartmentName|Email",
        fields are optional but vertical bar is required, multiple recipients
        are separated by "^@^".
        '''
        res = ''
        for recipient in recipients:
            if res != '':
                res += '^@^'
            if not self.recipient_is_email(recipient):
                raise BadRequest('邮箱地址无效')
            res += f'||||{recipient}'
        return res
