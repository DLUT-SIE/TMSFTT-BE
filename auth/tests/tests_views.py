'''Unit tests for auth views.'''
from django.contrib.auth import get_user_model
from django.urls import reverse
from model_mommy import mommy
from rest_framework import status
from rest_framework.test import APITestCase

import auth.models
from auth.utils import assign_perm


User = get_user_model()


class TestDepartmentViewSet(APITestCase):
    '''Unit tests for Department view.'''
    @classmethod
    def setUpTestData(cls):
        cls.user = mommy.make(User)
        assign_perm('tmsftt_auth.add_department', cls.user)
        assign_perm('tmsftt_auth.delete_department', cls.user)
        assign_perm('tmsftt_auth.change_department', cls.user)
        assign_perm('tmsftt_auth.view_department', cls.user)

    def test_list_department(self):
        '''Departments list should be accessed by GET request.'''
        url = reverse('department-list')

        self.client.force_authenticate(self.user)
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_department(self):
        '''Department should be accessed by GET request.'''
        department = mommy.make(auth.models.Department)
        url = reverse('department-detail', args=(department.pk,))
        expected_keys = {'id', 'name', 'users', 'admins'}

        self.client.force_authenticate(self.user)
        assign_perm('view_department', self.user, department)
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(set(response.data.keys()), expected_keys)


class TestUserViewSet(APITestCase):
    '''Unit tests for User view.'''
    @classmethod
    def setUpTestData(cls):
        cls.user = mommy.make(User, is_staff=True)
        assign_perm('tmsftt_auth.add_user', cls.user)
        assign_perm('tmsftt_auth.delete_user', cls.user)
        assign_perm('tmsftt_auth.change_user', cls.user)
        assign_perm('tmsftt_auth.view_user', cls.user)

    def test_list_user(self):
        '''Should return all users if user is admin.'''
        url = reverse('user-list')

        self.client.force_authenticate(self.user)
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
