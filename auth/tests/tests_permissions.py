'''Unit tests for permissions.'''
from unittest.mock import Mock
from django.test import TestCase


import auth.permissions as permissions


class TestSuperAdminOnlyPermission(TestCase):
    '''Unit tests for SuperAdminOnlyPermission.'''
    def test_unauthenticated_user(self):
        '''Should False if user hasn't been authenticated.'''
        request = Mock()
        request.user = Mock()
        request.user.is_authenticated = False
        permission = permissions.SuperAdminOnlyPermission()

        has_permission = permission.has_permission(request, None)

        self.assertFalse(has_permission)

    def test_non_superadmin_user(self):
        '''Should False if user isn't superadmin.'''
        request = Mock()
        request.user = Mock()
        request.user.is_authenticated = True
        request.user.is_superadmin = False
        permission = permissions.SuperAdminOnlyPermission()

        has_permission = permission.has_permission(request, None)

        self.assertFalse(has_permission)

    def test_superadmin_user(self):
        '''Should True if user is superadmin.'''
        request = Mock()
        request.user = Mock()
        request.user.is_authenticated = True
        request.user.is_superadmin = True
        permission = permissions.SuperAdminOnlyPermission()

        has_permission = permission.has_permission(request, None)

        self.assertTrue(has_permission)


class TestDepartmentAdminOnlyPermission(TestCase):
    '''Unit tests for DepartmentAdminOnlyPermission.'''
    def test_unauthenticated_user(self):
        '''Should False if user hasn't been authenticated.'''
        request = Mock()
        request.user = Mock()
        request.user.is_authenticated = False
        permission = permissions.DepartmentAdminOnlyPermission()

        has_permission = permission.has_permission(request, None)

        self.assertFalse(has_permission)

    def test_non_dept_admin_user(self):
        '''Should False if user isn't department admin.'''
        request = Mock()
        request.user = Mock()
        request.user.is_authenticated = True
        request.user.is_dept_admin = False
        permission = permissions.DepartmentAdminOnlyPermission()

        has_permission = permission.has_permission(request, None)

        self.assertFalse(has_permission)

    def test_dept_admin_user(self):
        '''Should True if user is department admin.'''
        request = Mock()
        request.user = Mock()
        request.user.is_authenticated = True
        request.user.is_dept_admin = True
        permission = permissions.DepartmentAdminOnlyPermission()

        has_permission = permission.has_permission(request, None)

        self.assertTrue(has_permission)


class TestTeacherOnlyPermission(TestCase):
    '''Unit tests for TeacherOnlyPermission.'''
    def test_unauthenticated_user(self):
        '''Should False if user hasn't been authenticated.'''
        request = Mock()
        request.user = Mock()
        request.user.is_authenticated = False
        permission = permissions.TeacherOnlyPermission()

        has_permission = permission.has_permission(request, None)

        self.assertFalse(has_permission)

    def test_non_teacher_user(self):
        '''Should False if user isn't teacher.'''
        request = Mock()
        request.user = Mock()
        request.user.is_authenticated = True
        request.user.is_teacher = False
        permission = permissions.TeacherOnlyPermission()

        has_permission = permission.has_permission(request, None)

        self.assertFalse(has_permission)

    def test_teacher_user(self):
        '''Should True if user is teacher.'''
        request = Mock()
        request.user = Mock()
        request.user.is_authenticated = True
        request.user.is_teacher = True
        permission = permissions.TeacherOnlyPermission()

        has_permission = permission.has_permission(request, None)

        self.assertTrue(has_permission)
