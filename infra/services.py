'''Provide services of infra module.'''
from django.utils.timezone import now

from infra.models import Notification


class NotificationService:  # pylint: disable=R0903
    '''Provide services for Notification.'''
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
        return Notification.objects.filter(recipient=user).delete()
