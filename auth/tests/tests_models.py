from unittest.mock import patch

from django.test import TestCase

from auth.models import Department, UserProfile


class TestDepartment(TestCase):
    def test_str(self):
        name = 'name'

        department = Department(name=name)

        self.assertEqual(str(department), name)


class TestUserProfile(TestCase):
    @patch('auth.models.UserProfile.user')
    def test_str(self, mocked_user):
        name = 'name'
        mocked_user.__str__.return_value = name

        profile = UserProfile()

        self.assertEqual(str(profile), name)
