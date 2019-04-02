'''Provide API views for auth module.'''
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from rest_framework import viewsets, mixins, permissions

import auth.models
import auth.serializers


User = get_user_model()


class DepartmentViewSet(viewsets.ModelViewSet):
    '''Create API views for Department.'''
    queryset = auth.models.Department.objects.all()
    serializer_class = auth.serializers.DepartmentSerializer


class UserViewSet(mixins.RetrieveModelMixin,
                  mixins.ListModelMixin,
                  viewsets.GenericViewSet):
    '''Create API views for User.'''
    queryset = User.objects.all()
    serializer_class = auth.serializers.UserSerializer
    filter_fields = ('username',)
    permission_classes = (permissions.IsAuthenticated,)

    def get_queryset(self):
        '''Filter queryset against role.'''
        user = self.request.user
        queryset = super().get_queryset()
        # TODO(youchen): Should we check based on other info
        if user.is_staff:
            return queryset
        return queryset.filter(pk=user.pk)


class UserPermissionViewSet(mixins.CreateModelMixin,
                            mixins.ListModelMixin,
                            mixins.RetrieveModelMixin,
                            mixins.DestroyModelMixin,
                            viewsets.GenericViewSet):
    '''Create API views for UserPermission.'''
    queryset = (auth.models.UserPermission.objects.all()
                .select_related('permission'))
    serializer_class = auth.serializers.UserPermissionSerializer
    filter_fields = ('user',)
    pagination_class = None


class PermissionViewSet(viewsets.ReadOnlyModelViewSet):
    '''Create READ-ONLY APIs for Permission.'''
    # Exclude Django-admin-related permissions.
    queryset = Permission.objects.filter(content_type_id__gt=6).all()
    serializer_class = auth.serializers.PermissionSerializer
    pagination_class = None
