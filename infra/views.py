'''Provide API views for infra module.'''
from rest_framework import mixins, viewsets

import infra.models
import infra.serializers


class NotificationViewSet(mixins.ListModelMixin,
                          mixins.RetrieveModelMixin,
                          viewsets.GenericViewSet):
    '''Create API views for Notification.'''
    queryset = infra.models.Notification.objects.all()
    serializer_class = infra.serializers.NotificationSerializer
