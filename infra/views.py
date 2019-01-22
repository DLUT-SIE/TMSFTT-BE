'''Provide API views for infra module.'''
from rest_framework import mixins, viewsets, decorators
from rest_framework.response import Response

import infra.models
import infra.serializers


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

    @decorators.action(detail=False, url_path='unread')
    def unread(self, request):
        '''Return notifications which are not read yet.'''
        return self._get_read_status_filtered_notifications(request, False)

    @decorators.action(detail=False, url_path='read')
    def read(self, request):
        '''Return notifications which are already read.'''
        return self._get_read_status_filtered_notifications(request, True)
