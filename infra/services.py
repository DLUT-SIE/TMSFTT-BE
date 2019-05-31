'''Provide services of infra module.'''
from django.utils.timezone import now
from django.contrib.auth import get_user_model

from infra.models import Notification
from infra.utils import prod_logger


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
