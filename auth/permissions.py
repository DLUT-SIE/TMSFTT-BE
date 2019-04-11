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


class DjangoModelPermissions(permissions.DjangoModelPermissions):
    '''Require model permissions for resources.'''
    perms_map = permissions.DjangoModelPermissions.perms_map
    perms_map.update({
        'GET': ['%(app_label)s.view_%(model_name)s'],
        'OPTIONS': ['%(app_label)s.view_%(model_name)s'],
        'HEAD': ['%(app_label)s.view_%(model_name)s'],
    })


class DjangoObjectPermissions(permissions.DjangoObjectPermissions):
    '''Require object permissions for resources.'''
    perms_map = permissions.DjangoObjectPermissions.perms_map
    perms_map.update({
        'GET': ['%(app_label)s.view_%(model_name)s'],
        'OPTIONS': ['%(app_label)s.view_%(model_name)s'],
        'HEAD': ['%(app_label)s.view_%(model_name)s'],
    })
