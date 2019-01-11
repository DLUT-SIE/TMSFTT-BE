'''Unit tests for auth serializers.'''
from django.contrib.auth.models import User
from django.test import TestCase

import auth.serializers as serializers
import auth.models as models


class TestUserSerializer(TestCase):
    '''Unit tests for serializer of User.'''
    def test_fields_equal(self):
        '''Serializer should return fields of User correctly.'''
        user = User()
        expected_keys = {
            'id', 'last_login', 'first_name', 'last_name', 'email',
            'is_active', 'date_joined'}

        keys = set(serializers.UserSerializer(user).data.keys())
        self.assertEqual(keys, expected_keys)


class TestDepartmentSerializer(TestCase):
    '''Unit tests for serializer of Department.'''
    def test_fields_equal(self):
        '''Serializer should return fields of Department correctly.'''
        department = models.Department()
        expected_keys = {'id', 'create_time', 'update_time', 'name', 'admins'}

        keys = set(serializers.DepartmentSerializer(department).data.keys())
        self.assertEqual(keys, expected_keys)


class TestUserProfileSerializer(TestCase):
    '''Unit tests for serializer of UserProfile.'''
    def test_fields_equal(self):
        '''Serializer should return fields of UserProfile correctly.'''
        profile = models.UserProfile()
        expected_keys = {'id', 'create_time', 'update_time', 'user',
                         'department', 'age'}

        keys = set(serializers.UserProfileSerializer(profile).data.keys())
        self.assertEqual(keys, expected_keys)
