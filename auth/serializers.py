'''Define how to serialize our models.'''
from django.contrib.auth import get_user_model
from rest_framework import serializers

import auth.models


User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    '''Indicate how to serialize User instance.'''
    class Meta:
        model = User
        fields = ('id', 'last_login', 'first_name', 'last_name', 'email',
                  'is_active', 'date_joined')


class DepartmentSerializer(serializers.ModelSerializer):
    '''Indicate how to serialize Department instance.'''
    class Meta:
        model = auth.models.Department
        fields = '__all__'


class UserProfileSerializer(serializers.ModelSerializer):
    '''Indicate how to serialize UserProfile instance.'''
    class Meta:
        model = auth.models.UserProfile
        fields = '__all__'
