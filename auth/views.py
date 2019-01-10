from rest_framework import viewsets

import auth.models
import auth.serializers


class DepartmentViewSet(viewsets.ModelViewSet):
    '''Create API views for Department.'''
    queryset = auth.models.Department.objects.all()
    serializer_class = auth.serializers.DepartmentSerializer


class UserProfileViewSet(viewsets.ModelViewSet):
    '''Create API views for UserProfile.'''
    queryset = auth.models.UserProfile.objects.all()
    serializer_class = auth.serializers.UserProfileSerializer
