'''REST permission checkers.'''
from rest_framework import permissions


class SuperAdminOnlyPermission(permissions.BasePermission):
    '''Only superadmin has access to resources.'''
    message = '需要拥有学校管理员身份才能访问。'

    def has_permission(self, request, view):
        '''Check super admin role.'''
        return request.user.is_authenticated and request.user.is_superadmin


class DepartmentAdminOnlyPermission(permissions.BasePermission):
    '''Only department admin has access to resources.'''
    message = '需要拥有二级管理员身份才能访问。'

    def has_permission(self, request, view):
        '''Check department admin role.'''
        return (request.user.is_authenticated
                and request.user.is_department_admin)


class TeacherOnlyPermission(permissions.BasePermission):
    '''Only teacher has access to resources.'''
    message = '需要拥有专任教师身份才能访问。'

    def has_permission(self, request, view):
        '''Check teacher role.'''
        return request.user.is_authenticated and request.user.is_teacher
