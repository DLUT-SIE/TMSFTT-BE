'''Provide services for infra module.'''
from django.utils.timezone import now

from infra.models import Notification


class NotificationService:  # pylint: disable=R0903
    '''Provide services for Notification.'''
    @staticmethod
    def mark_user_notifications_as_read(user_pk):
        '''Mark all notifications for user as read.'''
        notifications = (
            Notification.objects
            .filter(recipient__pk=user_pk)  # Notifications for current user
            .filter(read_time=None)  # All unread notifications
        )
        notifications.update(read_time=now())

    @staticmethod
    def delete_user_notifications(user_pk):
        '''Delete all notifications the current user received.'''
        notifications = Notification.objects.filter(recipient__pk=user_pk)
        notifications.delete()
