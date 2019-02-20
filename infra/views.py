'''Provide API views for infra module.'''
from rest_framework import mixins, viewsets, decorators, status, permissions
from rest_framework.response import Response
from django.conf import settings
from django.views.static import serve

import infra.models
import infra.serializers
from infra.services import NotificationService
from auth.permissions import CurrentUser


class NotificationViewSet(mixins.ListModelMixin,
                          mixins.RetrieveModelMixin,
                          viewsets.GenericViewSet):
    '''Create API views for Notification.'''
    queryset = infra.models.Notification.objects.all().order_by('-time')
    serializer_class = infra.serializers.NotificationSerializer

    def get_queryset(self):
        '''Filter against current user.'''
        user = self.request.user if hasattr(self.request, 'user') else None
        queryset = super().get_queryset()
        if user is None or user.is_authenticated is False:
            return queryset.none()
        return queryset.filter(recipient=user)

    def _get_read_status_filtered_notifications(self, request, is_read):
        '''Return filtered notifications based on read status.'''
        queryset = self.filter_queryset(self.get_queryset())
        if is_read:
            queryset = queryset.exclude(read_time=None)
        else:
            queryset = queryset.filter(read_time=None)

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @decorators.action(detail=False, methods=['GET'], url_path='unread')
    def unread(self, request):
        '''Return notifications which are not read yet.'''
        return self._get_read_status_filtered_notifications(request, False)

    @decorators.action(detail=False, methods=['GET'], url_path='read')
    def read(self, request):
        '''Return notifications which are already read.'''
        return self._get_read_status_filtered_notifications(request, True)


# pylint: disable=R0201
class NotificationUserTaskViewSet(viewsets.ViewSet):
    '''Create APIs for users tasks related to Notification.'''
    permission_classes = (permissions.IsAuthenticated, CurrentUser)

    @decorators.action(detail=False, methods=['POST'],
                       url_path='mark-all-notifications-as-read')
    def mark_all_notifications_as_read(self, request, user_pk=None):
        '''Mark all notifications the current user received as read.'''
        NotificationService.mark_user_notifications_as_read(int(user_pk))
        return Response(status=status.HTTP_201_CREATED)

    @decorators.action(detail=False, methods=['POST'],
                       url_path='delete-all-notifications')
    def delete_all_notifications(self, request, user_pk=None):
        '''Delete all notifications the current user received.'''
        NotificationService.delete_user_notifications(int(user_pk))
        return Response(status=status.HTTP_201_CREATED)


def index_view(request, *args, **kwargs):  # pragma: no cover
    '''DEBUG-only, return index page.'''
    return serve(request, 'index.html',
                 document_root=settings.BASE_DIR + '/static')
