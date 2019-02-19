'''Provide API views for auth module.'''
from django.contrib.auth import get_user_model
from rest_framework import viewsets, mixins, permissions
from rest_framework_bulk.mixins import (
    BulkCreateModelMixin,
    BulkDestroyModelMixin,
)

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
    permission_classes = (permissions.IsAuthenticated,)

    def get_queryset(self):
        '''Filter queryset against role.'''
        user = self.request.user
        queryset = super().get_queryset()
        # TODO(youchen): Should we check based on other info
        if user.is_staff:
            return queryset
        return queryset.filter(pk=user.pk)


class UserProfileViewSet(viewsets.ModelViewSet):
    '''Create API views for UserProfile.'''
    queryset = auth.models.UserProfile.objects.all()
    serializer_class = auth.serializers.UserProfileSerializer


class UserPermissionViewSet(BulkCreateModelMixin,
                            BulkDestroyModelMixin,
                            mixins.CreateModelMixin,
                            mixins.ListModelMixin,
                            mixins.RetrieveModelMixin,
                            mixins.DestroyModelMixin,
                            viewsets.GenericViewSet):
    '''Create API views for UserPermission.'''
    queryset = (auth.models.UserPermission.objects.all()
                .select_related('permission'))
    serializer_class = auth.serializers.UserPermissionSerializer
