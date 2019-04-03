'''Unit tests for auth models.'''
from django.test import TestCase

from auth.models import User, Department, UserPermission, Role


class TestUser(TestCase):
    '''Unit tests for model User.'''
    def test_str(self):
        '''Should render string correctly.'''
        username = 'name'

        user = User(username=username)

        self.assertEqual(str(user), username)


class TestDepartment(TestCase):
    '''Unit tests for model Department.'''
    def test_str(self):
        '''Should render string correctly.'''
        name = 'name'

        department = Department(name=name)

        self.assertEqual(str(department), name)


class TestUserPermission(TestCase):
    '''Unit tests for model UserPermission.'''
    def test_str(self):
        '''Should render string correctly.'''
        user_id = 1
        permission_id = 2
        expected_str = '用户{}拥有权限{}'.format(user_id, permission_id)

        user_permission = UserPermission(
            user_id=user_id,
            permission_id=permission_id)

        self.assertEqual(str(user_permission), expected_str)


class TestRole(TestCase):
    '''Unit tests for model Role.'''
    def test_str(self):
        '''Should render string correctly.'''
        type, name = Role.ROLE_CHOICES[0]
        role = Role(type=type)

        self.assertEqual(str(role), name)

