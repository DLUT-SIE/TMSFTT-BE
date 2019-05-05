'''Provide API views for auth module.'''
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission, Group
from rest_framework import viewsets, mixins

import auth.models
import auth.serializers
import auth.permissions
import auth.filters

User = get_user_model()


class DepartmentViewSet(viewsets.ReadOnlyModelViewSet):
    '''Create API views for Department.'''
    queryset = auth.models.Department.objects.all()
    serializer_class = auth.serializers.DepartmentSerializer
    permission_classes = (
        auth.permissions.DjangoModelPermissions,
        auth.permissions.DjangoObjectPermissions,
    )


class UserViewSet(mixins.RetrieveModelMixin,
                  mixins.ListModelMixin,
                  viewsets.GenericViewSet):
    '''Create API views for User.'''
    queryset = (User.objects
                .select_related('department')
                .prefetch_related('user_permissions')
                .all())
    serializer_class = auth.serializers.UserSerializer
    permission_classes = (
        auth.permissions.DjangoModelPermissions,
        auth.permissions.DjangoObjectPermissions,
    )
    filter_fields = ('username', 'groups')


class GroupViewSet(mixins.ListModelMixin,
                   viewsets.GenericViewSet):
    '''Create API views for Group.'''
    queryset = Group.objects.all()
    serializer_class = auth.serializers.GroupSerializer
    permission_classes = (
        auth.permissions.SchoolAdminOnlyPermission,
    )
    filter_class = auth.filters.GroupFilter


class GroupPermissionViewSet(mixins.CreateModelMixin,
                             mixins.ListModelMixin,
                             mixins.RetrieveModelMixin,
                             mixins.DestroyModelMixin,
                             viewsets.GenericViewSet):
    '''Create API views for GroupPermission.'''
    queryset = (auth.models.GroupPermission.objects.all())
    serializer_class = auth.serializers.GroupPermissionSerializer
    permission_classes = (
        auth.permissions.SchoolAdminOnlyPermission,
    )
    filter_fields = ('group',)


class UserPermissionViewSet(mixins.CreateModelMixin,
                            mixins.ListModelMixin,
                            mixins.RetrieveModelMixin,
                            mixins.DestroyModelMixin,
                            viewsets.GenericViewSet):
    '''Create API views for UserPermission.'''
    queryset = (auth.models.UserPermission.objects
                .select_related('permission', 'user')
                .all())
    serializer_class = auth.serializers.UserPermissionSerializer
    permission_classes = (
        auth.permissions.SchoolAdminOnlyPermission,
    )
    filter_fields = ('user',)


class PermissionViewSet(viewsets.ReadOnlyModelViewSet):
    '''Create READ-ONLY APIs for Permission.'''
    # Exclude Django-admin-related permissions.
    queryset = Permission.objects.filter(content_type_id__gt=13).all()
    serializer_class = auth.serializers.PermissionSerializer
    permission_classes = (
        auth.permissions.SchoolAdminOnlyPermission,
    )
