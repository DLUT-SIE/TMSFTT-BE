'''Unit tests for auth views.'''
from django.contrib.auth import get_user_model
from django.urls import reverse
from model_mommy import mommy
from rest_framework import status
from rest_framework.test import APITestCase

import auth.models


User = get_user_model()


class TestDepartmentViewSet(APITestCase):
    '''Unit tests for Department view.'''
    def test_create_department(self):
        '''Department should be created by POST request.'''
        url = reverse('department-list')
        name = 'department'
        data = {'name': name}

        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(auth.models.Department.objects.count(), 1)
        self.assertEqual(auth.models.Department.objects.get().name, name)

    def test_list_department(self):
        '''Departments list should be accessed by GET request.'''
        url = reverse('department-list')

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_delete_department(self):
        '''Department should be deleted by DELETE request.'''
        department = mommy.make(auth.models.Department)
        url = reverse('department-detail', args=(department.pk,))

        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(auth.models.Department.objects.count(), 0)

    def test_get_department(self):
        '''Department should be accessed by GET request.'''
        department = mommy.make(auth.models.Department)
        url = reverse('department-detail', args=(department.pk,))
        expected_keys = {'id', 'create_time', 'update_time', 'name',
                         'permissions', 'users'}

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(set(response.data.keys()), expected_keys)

    def test_update_department(self):
        '''Department should be updated by PATCH request.'''
        name0 = 'department0'
        name1 = 'department1'
        department = mommy.make(auth.models.Department, name=name0)
        url = reverse('department-detail', args=(department.pk,))
        data = {'name': name1}

        response = self.client.patch(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('name', response.data)
        self.assertEqual(response.data['name'], name1)


class TestUserViewSet(APITestCase):
    '''Unit tests for User view.'''
    def test_list_user_as_admin(self):
        '''Should return all users if user is admin.'''
        admin = mommy.make(User, is_staff=True)
        count = 10
        for _ in range(count):
            mommy.make(User)
        url = reverse('user-list')

        self.client.force_authenticate(admin)
        response = self.client.get(url, {'limit': count + 1})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), count + 1)

    def test_list_user_as_normal_user(self):
        '''Should return itself if user is not admin.'''
        user = mommy.make(User, is_staff=False)
        count = 10
        for _ in range(count):
            mommy.make(User)
        url = reverse('user-list')

        self.client.force_authenticate(user)
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
