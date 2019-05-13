'''Unit tests for permissions.'''
from unittest.mock import Mock, patch, call
from django.test import TestCase
from django.http import Http404
from rest_framework import exceptions

import auth.permissions as permissions


class TestSchoolAdminOnlyPermission(TestCase):
    '''Unit tests for SchoolAdminOnlyPermission.'''
    def test_unauthenticated_user(self):
        '''Should False if user hasn't been authenticated.'''
        request = Mock()
        request.user = Mock()
        request.user.is_authenticated = False
        permission = permissions.SchoolAdminOnlyPermission()

        has_permission = permission.has_permission(request, None)

        self.assertFalse(has_permission)

    def test_non_schooladmin_user(self):
        '''Should False if user isn't school admin.'''
        request = Mock()
        request.user = Mock()
        request.user.is_authenticated = True
        request.user.is_school_admin = False
        permission = permissions.SchoolAdminOnlyPermission()

        has_permission = permission.has_permission(request, None)

        self.assertFalse(has_permission)

    def test_schooladmin_user(self):
        '''Should True if user is school admin.'''
        request = Mock()
        request.user = Mock()
        request.user.is_authenticated = True
        request.user.is_school_admin = True
        permission = permissions.SchoolAdminOnlyPermission()

        has_permission = permission.has_permission(request, None)

        self.assertTrue(has_permission)


class TestDeparmentAdminOnlyPermission(TestCase):
    '''Unit tests for DepartmentAdminOnlyPermission.'''
    def test_unauthenticated_user(self):
        '''Should False if user hasn't been authenticated.'''
        request = Mock()
        request.user = Mock()
        request.user.is_authenticated = False
        permission = permissions.DepartmentAdminOnlyPermission()

        has_permission = permission.has_permission(request, None)

        self.assertFalse(has_permission)

    def test_non_departmentadmin_user(self):
        '''Should False if user isn't school admin.'''
        request = Mock()
        request.user = Mock()
        request.user.is_authenticated = True
        request.user.is_department_admin = False
        permission = permissions.DepartmentAdminOnlyPermission()

        has_permission = permission.has_permission(request, None)

        self.assertFalse(has_permission)

    def test_deparmentadmin_user(self):
        '''Should True if user is school admin.'''
        request = Mock()
        request.user = Mock()
        request.user.is_authenticated = True
        request.user.is_deparment_admin = True
        permission = permissions.DepartmentAdminOnlyPermission()

        has_permission = permission.has_permission(request, None)

        self.assertTrue(has_permission)


class TestDjangoModelPermissions(TestCase):
    '''Test permissions for model.'''
    @classmethod
    def setUpTestData(cls):
        model_cls = Mock()
        model_cls._meta.app_label = 'my_app'
        model_cls._meta.model_name = 'FakeModel'
        cls.model_cls = model_cls

    def test_get_required_permission_invalid_method(self):
        '''Should raise MethodNotAllowed if method not in perms_map.'''
        permission = permissions.DjangoModelPermissions()
        method = 'method-does-not-exist'

        with self.assertRaisesMessage(exceptions.MethodNotAllowed, method):
            permission.get_required_permissions(method, Mock(), self.model_cls)

    def test_get_required_permission_default_all(self):
        '''Should return default permissions if no `perms_map` on view.'''
        permission = permissions.DjangoModelPermissions()
        method = 'GET'
        view = Mock()
        view.action = 'retrieve'
        view.perms_map = {}
        _meta = self.model_cls._meta
        expected_perms = [f'{_meta.app_label}.view_{_meta.model_name}']

        perms = permission.get_required_permissions(
            method, view, self.model_cls)

        self.assertEqual(perms, expected_perms)

    def test_get_required_permission_default_action_custom_permission(self):
        '''Should return custom permissions if `perms_map` on view.'''
        permission = permissions.DjangoModelPermissions()
        method = 'GET'
        view = Mock()
        view.action = 'retrieve'
        view.perms_map = {
            'retrieve': ['%(app_label)s.custom_permission']
        }
        expected_perms = [
            f'{self.model_cls._meta.app_label}.custom_permission']

        perms = permission.get_required_permissions(
            method, view, self.model_cls)

        self.assertEqual(perms, expected_perms)

    def test_get_required_permission_custom_action(self):
        '''
        Should return permissions for custom action if `perms_map` on view.
        '''
        permission = permissions.DjangoModelPermissions()
        method = 'POST'
        view = Mock()
        view.action = 'custom-action'
        view.perms_map = {
            'custom-action': ['%(app_label)s.custom_permission']
        }
        expected_perms = [
            f'{self.model_cls._meta.app_label}.custom_permission']

        perms = permission.get_required_permissions(
            method, view, self.model_cls)

        self.assertEqual(perms, expected_perms)

    @patch('auth.permissions.prod_logger')
    def test_get_required_permission_custom_action_no_perms_map(self, _):
        '''
        Should raise PermissionDenied for custom action if no `perms_map`.
        '''
        permission = permissions.DjangoModelPermissions()
        method = 'POST'
        view = Mock(spec_set=['action'])
        view.action = 'custom-action'

        with self.assertRaises(exceptions.PermissionDenied):
            permission.get_required_permissions(method, view, self.model_cls)

    @patch('auth.permissions.prod_logger')
    def test_get_required_permission_custom_action_no_permission(self, _):
        '''
        Should raise PermissionDenied for custom action if no permissions are
        configured in `perms_map`.
        '''
        permission = permissions.DjangoModelPermissions()
        method = 'POST'
        view = Mock(spec_set=['action', 'perms_map'])
        view.action = 'custom-action'
        view.perms_map = {}

        with self.assertRaises(exceptions.PermissionDenied):
            permission.get_required_permissions(method, view, self.model_cls)

    def test_has_permission_for_workaround(self):
        '''Should return True for a workaround as described.'''
        view = Mock()
        # pylint: disable=protected-access
        view._ignore_model_permission = True
        request = Mock()
        permission = permissions.DjangoModelPermissions()

        has_perm = permission.has_permission(request, view)

        self.assertTrue(has_perm)

    def test_has_permission_unauthenticated(self):
        '''Should return False for if user is not authenticated.'''
        view = Mock(spec_set=[])
        request = Mock()
        request.user.is_authenticated = False
        permission = permissions.DjangoModelPermissions()

        has_perm = permission.has_permission(request, view)

        self.assertFalse(has_perm)

    @patch('auth.permissions.DjangoModelPermissions.get_required_permissions')
    @patch('auth.permissions.DjangoModelPermissions._queryset')
    def test_has_permission(self, _, mocked_get):
        '''Should return False for if user is not authenticated.'''
        view = Mock(spec_set=[])
        request = Mock()
        request.user.is_authenticated = True
        request.user.has_perms.return_value = True
        permission = permissions.DjangoModelPermissions()
        perms = ['perm_name']
        mocked_get.return_value = perms

        has_perm = permission.has_permission(request, view)

        self.assertTrue(has_perm)
        request.user.has_perms.assert_called_with(perms)


class TestDjangoObjectPermissions(TestCase):
    '''Test permissions for object.'''
    @classmethod
    def setUpTestData(cls):
        model_cls = Mock()
        model_cls._meta.app_label = 'my_app'
        model_cls._meta.model_name = 'FakeModel'
        cls.model_cls = model_cls

    @patch('auth.permissions.DjangoObjectPermissions.get_required_permissions')
    def test_get_required_object_permission(self, mocked_get):
        '''Should call `get_required_permissions`.'''
        method = 'GET'
        view = Mock()
        permission = permissions.DjangoObjectPermissions()

        permission.get_required_object_permissions(
            method, view, self.model_cls)

        mocked_get.assert_called_with(method, view, self.model_cls)

    @patch(
        'auth.permissions.DjangoObjectPermissions'
        '.get_required_object_permissions')
    @patch('auth.permissions.DjangoModelPermissions._queryset')
    def test_has_object_permission_true(self, _, mocked_get):
        '''Should return True if user has permission.'''
        perms = ['permission_1', 'permission_2']
        mocked_get.return_value = perms
        request = Mock()
        request.user.has_perms.return_value = True
        view = Mock()
        obj = Mock()
        mocked_get.return_value = perms
        permission = permissions.DjangoObjectPermissions()

        has_perm = permission.has_object_permission(request, view, obj)

        mocked_get.assert_called()
        request.user.has_perms.assert_called_with(perms, obj)
        self.assertTrue(has_perm)

    @patch(
        'auth.permissions.DjangoObjectPermissions'
        '.get_required_object_permissions')
    @patch('auth.permissions.DjangoModelPermissions._queryset')
    def test_has_object_permission_404_safe(self, mocked_queryset, mocked_get):
        '''
        Should return 404 if user doesn't has permission with a safe method.'''
        perms = ['permission_1', 'permission_2']
        mocked_get.return_value = perms
        queryset = Mock()
        mocked_queryset.return_value = queryset
        request = Mock()
        request.method = 'GET'
        request.user.has_perms.return_value = False
        view = Mock()
        obj = Mock()
        mocked_get.return_value = perms
        permission = permissions.DjangoObjectPermissions()

        with self.assertRaises(Http404):
            permission.has_object_permission(request, view, obj)

        mocked_get.assert_called_with(request.method, view, queryset.model)
        request.user.has_perms.assert_called_with(perms, obj)

    @patch(
        'auth.permissions.DjangoObjectPermissions'
        '.get_required_object_permissions')
    @patch('auth.permissions.DjangoModelPermissions._queryset')
    def test_has_object_permission_404_unsafe_without_safe(
            self, mocked_queryset, mocked_get):
        '''
        Should return 404 if user doesn't has permission with an unsafe
        method, and has no GET permission.'''
        perms = ['permission_1', 'permission_2']
        read_perms = ['perm_1']
        mocked_get.return_value = perms
        queryset = Mock()
        mocked_queryset.return_value = queryset
        request = Mock()
        request.method = 'POST'
        request.user.has_perms.side_effect = [False, False]
        view = Mock()
        obj = Mock()
        mocked_get.side_effect = [perms, read_perms]
        permission = permissions.DjangoObjectPermissions()

        with self.assertRaises(Http404):
            permission.has_object_permission(request, view, obj)

        mocked_get.assert_has_calls([
            call(request.method, view, queryset.model),
            call('GET', view, queryset.model)
        ])
        request.user.has_perms.assert_has_calls([
            call(perms, obj),
            call(read_perms, obj),
        ])

    @patch(
        'auth.permissions.DjangoObjectPermissions'
        '.get_required_object_permissions')
    @patch('auth.permissions.DjangoModelPermissions._queryset')
    def test_has_object_permission_404_unsafe_with_safe(
            self, mocked_queryset, mocked_get):
        '''
        Should return 403 if user doesn't has permission with an unsafe
        method, but has GET permission.'''
        perms = ['permission_1', 'permission_2']
        read_perms = ['perm_1']
        mocked_get.return_value = perms
        queryset = Mock()
        mocked_queryset.return_value = queryset
        request = Mock()
        request.method = 'POST'
        request.user.has_perms.side_effect = [False, True]
        view = Mock()
        obj = Mock()
        mocked_get.side_effect = [perms, read_perms]
        permission = permissions.DjangoObjectPermissions()

        has_perm = permission.has_object_permission(request, view, obj)

        self.assertFalse(has_perm)
        mocked_get.assert_has_calls([
            call(request.method, view, queryset.model),
            call('GET', view, queryset.model)
        ])
        request.user.has_perms.assert_has_calls([
            call(perms, obj),
            call(read_perms, obj),
        ])
