'''Provide services of infra module.'''
import base64
import json
import hashlib

from django.conf import settings
from django.utils.timezone import now
from django.contrib.auth import get_user_model
from zeep import Client
from zeep.cache import InMemoryCache
from zeep.transports import Transport

from infra.models import Notification
from infra.utils import prod_logger
from infra.exceptions import InternalServerError


User = get_user_model()


class NotificationService:  # pylint: disable=R0903
    '''Provide services for Notification.'''
    @classmethod
    def _get_notification_robot(cls):
        robot = User.objects.get(username='notification-robot')
        return robot

    @staticmethod
    def mark_user_notifications_as_read(user):
        '''Mark all notifications for user as read.'''
        notifications = (
            Notification.objects
            .filter(recipient=user)  # Notifications for current user
            .filter(read_time=None)  # All unread notifications
        )
        return notifications.update(read_time=now())

    @staticmethod
    def delete_user_notifications(user):
        '''Delete all notifications the current user received.'''
        msg = f'正在删除用户 {user.first_name}(工号: {user.username}) 的所有通知'
        prod_logger.info(msg)
        return Notification.objects.filter(recipient=user).delete()

    @staticmethod
    def send_system_notification(recipient, content):
        '''Send system notification.

        Parameters
        ------------
        recipient: User or int,
            The user or the id of the user to receive the notification.
        content: str
            The content of the notification.
        '''
        if isinstance(recipient, int):
            recipient = User.objects.get(id=recipient)
        elif not isinstance(recipient, User):
            raise ValueError('Only User instance or int id is supported')
        notification = Notification.objects.create(
            sender=NotificationService._get_notification_robot(),
            recipient=recipient,
            content=content
        )
        from auth.services import PermissionService
        PermissionService.assign_object_permissions(recipient, notification)


class SOAPSMSService:
    '''Provide service for sending sms.'''
    def send_sms(self, smses):
        '''Send sms to user.

        Parameters
        ------------
        SMSes: list of dict,
            {
                'user_phone_number': String,
                'sms_info': String,
            }
        '''
        transport = Transport(cache=InMemoryCache())
        try:
            client = Client(
                f'{settings.SOAP_BASE_URL}/SmsService?wsdl',
                transport=transport
            )
        except Exception:
            prod_logger.warning('获取WSDL失败，短信服务暂时不可用')
            raise InternalServerError('短信服务暂时不可用')

        # According to the protocol, we need encrypt our secret_key with
        # SHA-1 and encode with base64
        sha1 = hashlib.sha1()
        sha1.update(settings.SOAP_AUTH_SECRET_KEY.encode())
        secret_key = base64.b64encode(sha1.digest())

        default_payload = {
            # Auth-related
            'tp_name': settings.SOAP_AUTH_TP_NAME,
            'sys_id': settings.SOAP_AUTH_SYS_ID,
            'module_id': 'sms',
            'secret_key': secret_key.decode(),
            'interface_method': 'sms',

            # Business-related
            # NOTE: recieve_person_info is the correct parameter name,
            # I know it's a typo but it's required by the interface
            'recieve_person_info': '',  # Required
            # NOTE: Again, emial_title is the correct parameter name
            'sms_info': '',  # Required
            'send_priority': '3',  # Send now
            'templet_id': '0',
            'receipt_id': '0',
            'send_sys_id': '1',
        }

        for sms in smses:
            phone_number = sms.get('user_phone')
            sms_info = sms.get('sms_info')
            payload = default_payload.copy()
            payload['recieve_person_info'] = self.format_recipients(
                phone_number)
            payload['sms_info'] = sms_info
            sms_info = json.dumps(payload)
            try:
                resp = client.service.saveSmsInfo(sms_info)
                resp = json.loads(resp)
                if resp['result'] is False:
                    raise Exception(resp['msg'])
            except Exception as err:
                msg = f'短信发送失败, 失败原因: {err}'
                prod_logger.warning(msg)
                raise InternalServerError('短信发送失败')
            else:
                msg = (
                    f'短信发送成功, 收件人: {phone_number}, '
                    f'消息ID: {resp["msg_id"]}'
                )
                prod_logger.info(msg)

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
            res += f'||||{recipient}'
        return res
