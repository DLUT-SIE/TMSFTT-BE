'''Unit tests for auth models.'''
from django.test import TestCase

from auth.models import Department, UserProfile, UserPermission


class TestDepartment(TestCase):
    '''Unit tests for model Department.'''
    def test_str(self):
        '''Should render string correctly.'''
        name = 'name'

        department = Department(name=name)

        self.assertEqual(str(department), name)


class TestUserProfile(TestCase):
    '''Unit tests for model UserProfile.'''
    def test_str(self):
        '''Should render string correctly.'''
        user_id = 123

        profile = UserProfile(user_id=user_id)

        self.assertEqual(str(profile), str(user_id))


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
