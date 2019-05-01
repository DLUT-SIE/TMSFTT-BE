'''Provide API views for infra module.'''
from rest_framework import mixins, viewsets, decorators, status, permissions
from rest_framework.response import Response
from rest_framework_guardian import filters

import auth.permissions
import infra.models
import infra.serializers
from infra.services import NotificationService


class NotificationViewSet(mixins.ListModelMixin,
                          mixins.RetrieveModelMixin,
                          viewsets.GenericViewSet):
    '''Create API views for Notification.'''
    queryset = infra.models.Notification.objects.all().order_by('-time')
    serializer_class = infra.serializers.NotificationSerializer
    filter_backends = (filters.DjangoObjectPermissionsFilter,)
    permission_classes = (
        auth.permissions.DjangoObjectPermissions,
    )

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


class NotificationActionViewSet(viewsets.ViewSet):
    '''Define actions for users to manipulate Notification objects.'''
    permission_classes = (permissions.IsAuthenticated,)

    @decorators.action(detail=False, methods=['POST'],
                       url_path='read-all')
    def read_all(self, request):
        '''Mark all notifications as done for user.'''
        count = NotificationService.mark_user_notifications_as_read(
            request.user)
        return Response({'count': count}, status=status.HTTP_201_CREATED)

    @decorators.action(detail=False, methods=['POST'],
                       url_path='delete-all')
    def delete_all(self, request):
        '''Delete all notifications for user.'''
        count = NotificationService.delete_user_notifications(request.user)
        return Response({'count': count}, status=status.HTTP_201_CREATED)
