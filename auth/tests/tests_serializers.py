'''Unit tests for auth serializers.'''
from unittest.mock import patch
from django.contrib.auth import get_user_model
from django.test import TestCase
from model_mommy import mommy

import auth.serializers as serializers
import auth.models as models


User = get_user_model()


# pylint: disable=no-self-use
class TestDepartmentSerializer(TestCase):
    '''Unit tests for serializer of Department.'''

    @patch('auth.models.Role.objects.filter')
    def test_get_admins_no_role(self, mocked_filter):
        '''Should return empty list if no such role.'''
        department = mommy.make(models.Department)
        serializer = serializers.DepartmentSerializer()
        mocked_filter.return_value = []

        admins = serializer.get_admins(department)

        self.assertEqual(admins, [])
        mocked_filter.assert_called()

    def test_get_admins(self):
        '''Should return list of ids if role exists.'''
        department = mommy.make(models.Department)
        role = mommy.make(
            models.Role,
            department_id=department.id,
            role_type=models.Role.ROLE_DEPT_ADMIN
        )
        cnt = 10
        users = [mommy.make(User, roles=[role]) for _ in range(cnt)]
        serializer = serializers.DepartmentSerializer()

        admins = set(serializer.get_admins(department))
        self.assertEqual(admins, set(user.id for user in users))
