'''Define how to serialize our models.'''
from django.contrib.auth import get_user_model
from rest_framework import serializers

import infra.models


User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    '''Indicate how to serialize User instance.'''
    class Meta:
        model = User
        fields = ('id', 'last_login', 'first_name', 'last_name', 'email',
                  'is_active', 'date_joined')


class OperationLogSerializer(serializers.ModelSerializer):
    '''Indicate how to serialize OperationLog instance.'''
    class Meta:
        model = infra.models.OperationLog
        fields = '__all__'


class NotificationSerializer(serializers.ModelSerializer):
    '''Indicate how to serialize Notification instance.'''
    class Meta:
        model = infra.models.Notification
        fields = '__all__'
