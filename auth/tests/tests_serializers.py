from django.contrib.auth.models import User
from django.test import TestCase

import auth.serializers as serializers
import auth.models as models


class TestUserSerializer(TestCase):
    def test_fields_equal(self):
        user = User()
        expected_keys = {
            'id', 'last_login', 'first_name', 'last_name', 'email',
            'is_active', 'date_joined'}

        keys = set(serializers.UserSerializer(user).data.keys())
        self.assertEqual(keys, expected_keys)


class TestDepartmentSerializer(TestCase):
    def test_fields_equal(self):
        department = models.Department()
        expected_keys = {'id', 'create_time', 'update_time', 'name', 'admins'}

        keys = set(serializers.DepartmentSerializer(department).data.keys())
        self.assertEqual(keys, expected_keys)


class TestUserProfileSerializer(TestCase):
    def test_fields_equal(self):
        profile = models.UserProfile()
        expected_keys = {'id', 'create_time', 'update_time', 'user',
                         'department', 'age'}

        keys = set(serializers.UserProfileSerializer(profile).data.keys())
        self.assertEqual(keys, expected_keys)
