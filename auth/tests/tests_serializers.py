'''Unit tests for auth serializers.'''
from django.contrib.auth import get_user_model
from django.test import TestCase
from model_mommy import mommy

import auth.serializers as serializers
import auth.models as models


User = get_user_model()


# pylint: disable=no-self-use
class TestUserSerializer(TestCase):
    '''Unit tests for serializer of User.'''

    def test_fields_equal(self):
        '''Serializer should return fields of User correctly.'''
        user = mommy.make(User, department=mommy.make(models.Department))
        expected_keys = {
            'id', 'username', 'last_login', 'first_name', 'last_name',
            'email', 'is_active', 'date_joined', 'user_permissions',
            'is_teacher', 'is_department_admin', 'is_superadmin',
            'department', 'department_str'}

        keys = set(serializers.UserSerializer(user).data.keys())
        self.assertEqual(keys, expected_keys)
