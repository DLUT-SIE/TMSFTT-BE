'''Provide API views for infra module.'''
from django.utils.timezone import now
from rest_framework import mixins, viewsets, decorators, status
from rest_framework.response import Response
from rest_framework_guardian import filters

import auth.permissions
import infra.models
import infra.serializers
from infra.services import NotificationService


class NotificationViewSet(viewsets.ReadOnlyModelViewSet):
    '''Create API views for Notification.'''
    queryset = (
        infra.models.Notification.objects
        .select_related('sender', 'recipient')
        .all().order_by('-time')
    )
    serializer_class = infra.serializers.NotificationSerializer
    filter_backends = (filters.DjangoObjectPermissionsFilter,)
    permission_classes = (
        auth.permissions.DjangoObjectPermissions,
    )
    perms_map = {
        'read': ['%(app_label)s.view_%(model_name)s'],
        'unread': ['%(app_label)s.view_%(model_name)s'],
        'mark_all_as_read': ['%(app_label)s.view_%(model_name)s'],
    }

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

    def get_object(self):
        '''We override this function to update notification read_time.'''
        obj = super().get_object()
        if not obj.read_time:
            # It's not so RESTful, since we update the resource in a GET
            # method, but it simplify our logic a lot.
            obj.read_time = now()
            obj.save()
        return obj

    @decorators.action(detail=False, methods=['POST'],
                       url_path='mark-all-as-read')
    def mark_all_as_read(self, request):
        '''Mark all notifications as read for user.'''
        count = NotificationService.mark_user_notifications_as_read(
            request.user)
        return Response({'count': count}, status=status.HTTP_201_CREATED)
