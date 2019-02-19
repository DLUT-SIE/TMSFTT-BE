'''Unit tests for auth models.'''
from unittest.mock import patch

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
    @patch('auth.models.UserProfile.user')
    def test_str(self, mocked_user):
        '''Should render string correctly.'''
        name = 'name'
        mocked_user.__str__.return_value = name

        profile = UserProfile()

        self.assertEqual(str(profile), name)


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
