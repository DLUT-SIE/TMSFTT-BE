'''Unit tests for auth views.'''
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group, Permission
from django.urls import reverse
from model_mommy import mommy
from rest_framework import status
from rest_framework.test import APITestCase

import auth.models

User = get_user_model()


class TestDepartmentViewSet(APITestCase):
    '''Unit tests for Department view.'''
    @classmethod
    def setUpTestData(cls):
        cls.user = mommy.make(User, is_staff=True)

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
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(set(response.data.keys()), expected_keys)

    def test_top_level_departments(self):
        '''test top level departments.'''
        url = reverse('department-top-level-departments')
        self.client.force_authenticate(self.user)
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)


class TestUserViewSet(APITestCase):
    '''Unit tests for User view.'''
    @classmethod
    def setUpTestData(cls):
        cls.user = mommy.make(User, is_staff=True)

    def test_list_user(self):
        '''Should return all users if user is admin.'''
        url = reverse('user-list')

        self.client.force_authenticate(self.user)
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)


class TestGroupViewSet(APITestCase):
    '''Unit tests for Group view.'''
    @classmethod
    def setUpTestData(cls):
        cls.user = mommy.make(User, is_superuser=True)

    def setUp(self):
        self.client.force_authenticate(self.user)

    def test_list_group(self):
        '''Should return all groups if user is admin.'''
        url = reverse('group-list')

        self.client.force_authenticate(self.user)
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_top_department_related_groups(self):
        '''test top department related groups'''
        url = reverse('group-top-department-related-groups')
        self.client.force_authenticate(self.user)
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_top_department_related_groups_incorrect_id(self):
        '''test top department related groups if id is incorrect'''
        url = reverse('group-top-department-related-groups')
        data = {
            'department_id': "www"
        }
        response = self.client.get(url, data=data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class TestUserGroupViewSet(APITestCase):
    '''Unit tests for UserGroup view.'''
    @classmethod
    def setUpTestData(cls):
        User.objects.get_or_create(
            username='notification-robot', defaults={'first_name': '系统通知'}
        )
        Group.objects.create(name='个人权限')
        cls.user = mommy.make(User, is_staff=True)

    def setUp(self):
        self.client.force_authenticate(self.user)

    def test_list_usergroup(self):
        '''Should return all user-groups if user is admin.'''
        url = reverse('usergroup-list')

        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_create_user_group(self):
        '''UserGroup should be created by POST request.'''
        url = reverse('usergroup-list')
        user = mommy.make(User)
        group = mommy.make(Group)
        data = {
            'user': user.id,
            'group': group.id,
        }

        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(auth.models.UserGroup.objects.count(), 1)

    def test_delete_user_group(self):
        '''UserGroup should be deleted by DELETE request.'''
        usergroup = mommy.make(auth.models.UserGroup)
        url = reverse('usergroup-detail', args=(usergroup.pk,))

        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(auth.models.UserGroup.objects.count(), 0)


class TestGroupPermissionViewSet(APITestCase):
    '''Unit tests for GroupPermission view.'''
    @classmethod
    def setUpTestData(cls):
        cls.user = mommy.make(User, is_staff=True)

    def setUp(self):
        self.client.force_authenticate(self.user)

    def test_list_group_permission(self):
        '''Should return all group_permissions if user is admin.'''
        url = reverse('grouppermission-list')

        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_create_group_permission(self):
        '''Group_permissions should be created by POST request.'''
        url = reverse('grouppermission-list')
        group = mommy.make(Group)
        permission = mommy.make(Permission)
        data = {
            'group': group.id,
            'permission': permission.id,
        }

        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(auth.models.GroupPermission.objects.count(), 1)

    def test_delete_group_permission(self):
        '''Group_permissions should be deleted by DELETE request.'''
        group_permission = mommy.make(auth.models.GroupPermission)
        url = reverse('grouppermission-detail', args=(group_permission.pk,))

        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(auth.models.GroupPermission.objects.count(), 0)


class TestUserPermissionViewSet(APITestCase):
    '''Unit tests for UserPermission view.'''
    @classmethod
    def setUpTestData(cls):
        cls.user = mommy.make(User, is_staff=True)

    def setUp(self):
        self.client.force_authenticate(self.user)

    def test_list_user_permission(self):
        '''Should return all user_permissions if user is admin.'''
        url = reverse('userpermission-list')

        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_create_user_permission(self):
        '''User_permissions should be created by POST request.'''
        url = reverse('userpermission-list')
        user = mommy.make(User)
        permission = mommy.make(Permission)
        data = {
            'user': user.id,
            'permission': permission.id,
        }

        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(auth.models.UserPermission.objects.count(), 1)

    def test_delete_user_permission(self):
        '''User_permissions should be deleted by DELETE request.'''
        user_permission = mommy.make(auth.models.UserPermission)
        url = reverse('userpermission-detail', args=(user_permission.pk,))

        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(auth.models.UserPermission.objects.count(), 0)


class TestPermissionViewSet(APITestCase):
    '''Unit tests for Permission view.'''
    @classmethod
    def setUpTestData(cls):
        cls.user = mommy.make(User, is_staff=True)

    def setUp(self):
        self.client.force_authenticate(self.user)

    def test_list_permission(self):
        '''Should return all permissions if user is admin.'''
        url = reverse('permission-list')

        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
