'''Unit tests for auth models.'''
from django.test import TestCase
from model_mommy import mommy

from auth.models import User, Department, UserPermission, Role, GroupPermission


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
        role_type, role_name = Role.ROLE_CHOICES[0]
        department = mommy.make(Department)
        name = '{}({})'.format(department, role_name)
        role = Role(department=department, role_type=role_type)

        self.assertEqual(str(role), name)


class TestGroupPermission(TestCase):
    '''Unit tests for model GroupPermission.'''
    def test_str(self):
        '''Should render string correctly.'''
        group_id = 1
        permission_id = 2
        expected_str = '用户组{}拥有权限{}'.format(group_id, permission_id)

        group_permission = GroupPermission(
            group_id=group_id,
            permission_id=permission_id)

        self.assertEqual(str(group_permission), expected_str)
