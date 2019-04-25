'''Mixin classes provided by infra module.'''


class MultiSerializerActionClassMixin:
    '''Find serializer class for different actions in DRF viewset.

    This mixin will try to find serializer class from property named
    `serializer_action_classes`, which is a dict mapping action name to
    serializer class. If no serializer class is found for action, then fallback
    to default `.get_serializer_class()` method.

    Examples
    --------
    Class MyViewSet(MultiSerializerActionClass, ModelViewSet):
        serializer_action_classes = {
            'list': MyListSerializer,
            'retrieve': MyRetrieveSerializer,
            'create': MyCreateSerializer,
            'custom_action': MyCustomActionSerializer,
        }

        @action
        def custom_action(self):
            pass
    '''
    serializer_action_classes = {}
    action = None

    def get_serializer_class(self):
        '''Overwrite default `.get_serializer_class()` method.'''
        serializer_cls = self.serializer_action_classes.get(self.action, None)
        if serializer_cls is not None:
            return serializer_cls
        return super().get_serializer_class()
