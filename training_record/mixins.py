'''Mixin classes provided by record module.'''
from training_record.serializers import (
    ReadOnlyRecordSerializer,
    RecordCreateSerializer,
)


class MultiSerializerActionClassMixin:
    '''Find serializer class for different actions in RecordViewSet.'''

    serializer_action_classes = {
        'list': ReadOnlyRecordSerializer,
        'retrieve': ReadOnlyRecordSerializer,
        'create': RecordCreateSerializer,
        'reviewed': ReadOnlyRecordSerializer,
    }
    action = None

    def get_serializer_class(self):
        '''Overwrite default `.get_serializer_class()` method.'''
        serializer_cls = self.serializer_action_classes.get(self.action, None)
        if serializer_cls is not None:
            return serializer_cls
        return ReadOnlyRecordSerializer
