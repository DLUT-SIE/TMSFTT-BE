from django.contrib.auth.models import User
from django.urls import reverse
from model_mommy import mommy
from rest_framework import status
from rest_framework.test import APITestCase

import auth.models


class TestDepartmentViewSet(APITestCase):
    def test_create_department(self):
        url = reverse('department-list')
        name = 'department'
        data = {'name': name}

        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(auth.models.Department.objects.count(), 1)
        self.assertEqual(auth.models.Department.objects.get().name, name)

    def test_list_department(self):
        url = reverse('department-list')

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_delete_department(self):
        department = mommy.make(auth.models.Department)
        url = reverse('department-detail', args=(department.pk,))

        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(auth.models.Department.objects.count(), 0)

    def test_get_department(self):
        department = mommy.make(auth.models.Department)
        url = reverse('department-detail', args=(department.pk,))
        expected_keys = {'id', 'create_time', 'update_time', 'name', 'admins'}

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(set(response.data.keys()), expected_keys)

    def test_update_department(self):
        name0 = 'department0'
        name1 = 'department1'
        department = mommy.make(auth.models.Department, name=name0)
        url = reverse('department-detail', args=(department.pk,))
        data = {'name': name1}

        response = self.client.patch(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('name', response.data)
        self.assertEqual(response.data['name'], name1)


class TestUserProfileViewSet(APITestCase):
    def test_create_user_profile(self):
        user = mommy.make(User)
        department = mommy.make(auth.models.Department)
        url = reverse('userprofile-list')
        age = 10
        data = {'user': user.id, 'department': department.id, 'age': age}

        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(auth.models.UserProfile.objects.count(), 1)
        self.assertEqual(auth.models.UserProfile.objects.get().user.id,
                         user.id)
        self.assertEqual(auth.models.UserProfile.objects.get().age, age)
        self.assertEqual(auth.models.UserProfile.objects.get().department.id,
                         department.id)

    def test_list_user_profile(self):
        url = reverse('userprofile-list')

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_delete_user_profile(self):
        user_profile = mommy.make(auth.models.UserProfile)
        url = reverse('userprofile-detail', args=(user_profile.pk,))

        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(auth.models.UserProfile.objects.count(), 0)

    def test_get_user_profile(self):
        user_profile = mommy.make(auth.models.UserProfile)
        url = reverse('userprofile-detail', args=(user_profile.pk,))
        expected_keys = {'id', 'create_time', 'update_time', 'user',
                         'department', 'age'}

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(set(response.data.keys()), expected_keys)

    def test_update_user_profile(self):
        age0 = 10
        age1 = 15
        user_profile = mommy.make(auth.models.UserProfile, age=age0)
        url = reverse('userprofile-detail', args=(user_profile.pk,))
        data = {'age': age1}

        response = self.client.patch(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('age', response.data)
        self.assertEqual(response.data['age'], age1)
