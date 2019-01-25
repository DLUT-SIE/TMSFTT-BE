'''Provide permission checkers.'''
from rest_framework import permissions


class CurrentUser(permissions.BasePermission):
    '''Check whether user is the user that the request declared.'''

    def has_permission(self, request, view):
        '''Check whether user has permission.'''
        if 'kwargs' not in request.parser_context:
            return False
        user_pk = int(request.parser_context['kwargs'].get('user_pk', '-1'))
        return user_pk is not None and request.user.pk == user_pk
