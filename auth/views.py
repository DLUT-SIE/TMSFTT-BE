'''Provide API views for auth module.'''
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from rest_framework import viewsets, mixins

import auth.models
import auth.serializers
import auth.permissions


User = get_user_model()


class DepartmentViewSet(viewsets.ModelViewSet):
    '''Create API views for Department.'''
    queryset = auth.models.Department.objects.all()
    serializer_class = auth.serializers.DepartmentSerializer
    permission_classes = (auth.permissions.SuperAdminOnlyPermission,)


class UserViewSet(mixins.RetrieveModelMixin,
                  mixins.ListModelMixin,
                  viewsets.GenericViewSet):
    '''Create API views for User.'''
    queryset = (User.objects
                .select_related('department')
                .prefetch_related('roles', 'user_permissions')
                .all())
    serializer_class = auth.serializers.UserSerializer
    permission_classes = (auth.permissions.SuperAdminOnlyPermission,)
    filter_fields = ('username',)


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
    permission_classes = (auth.permissions.SuperAdminOnlyPermission,)
    filter_fields = ('user',)
    pagination_class = None


class PermissionViewSet(viewsets.ReadOnlyModelViewSet):
    '''Create READ-ONLY APIs for Permission.'''
    # Exclude Django-admin-related permissions.
    queryset = Permission.objects.filter(content_type_id__gt=7).all()
    serializer_class = auth.serializers.PermissionSerializer
    permission_classes = (auth.permissions.SuperAdminOnlyPermission,)
    pagination_class = None
