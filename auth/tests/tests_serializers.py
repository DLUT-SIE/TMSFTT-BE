'''Unit tests for auth serializers.'''
from unittest.mock import patch
from django.contrib.auth import get_user_model
from django.test import TestCase
from model_mommy import mommy

import auth.serializers as serializers


User = get_user_model()


# pylint: disable=no-self-use
class TestUserSerializer(TestCase):
    '''Unit tests for serializer of User.'''
    def test_fields_equal(self):
        '''Serializer should return fields of User correctly.'''
        user = mommy.make(User)
        expected_keys = {
            'id', 'username', 'last_login', 'first_name', 'last_name',
            'email', 'is_active', 'date_joined', 'user_permissions',
            'is_teacher', 'is_dept_admin', 'is_superadmin'}

        keys = set(serializers.UserSerializer(user).data.keys())
        self.assertEqual(keys, expected_keys)

    @patch('auth.models.UserPermission.objects')
    @patch('auth.serializers.UserPermissionSerializer')
    def test_get_user_permissions(self, mocked_serialzier, mocked_objects):
        '''Serializer should query UserPermissions and serialize them.'''
        user = User()
        serializer = serializers.UserSerializer()

        serializer.get_user_permissions(user)

        mocked_serialzier.assert_called()
        mocked_objects.filter.assert_called_with(user=user)
