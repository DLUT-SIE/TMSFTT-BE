'''Unit tests for infra mixins.'''
from unittest.mock import Mock
from django.test import TestCase

from infra.mixins import MultiSerializerActionClassMixin


class TestMultiSerializerActionClassMixin(TestCase):
    '''Unit tests for MultiSerializerActionClassMixin.'''
    def setUp(self):
        # pylint: disable=missing-docstring
        class ViewSet:
            get_serializer_class = Mock()

        class MyViewSet(MultiSerializerActionClassMixin, ViewSet):
            serializer_action_classes = {
                'retrieve': Mock(),
            }

        self.viewset = MyViewSet()
        self.mocked_get_serializer_class = ViewSet.get_serializer_class

    def test_get_default_serializer_class(self):
        '''Should call default `.get_serializer_class()`.'''
        self.action = 'update'
        self.viewset.get_serializer_class()

        self.mocked_get_serializer_class.assert_called()

    def test_get_serializer_class_for_action(self):
        '''Should return serializer class for specifc action.'''
        self.viewset.action = 'retrieve'
        serializer_class = self.viewset.get_serializer_class()

        self.assertIs(
            serializer_class,
            self.viewset.serializer_action_classes['retrieve']
        )
