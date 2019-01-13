'''Define how to serialize our models.'''
from django.contrib.auth import get_user_model
from rest_framework import serializers

import training_record.models


User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    '''Indicate how to serialize User instance.'''
    class Meta:
        model = User
        fields = ('id', 'last_login', 'first_name', 'last_name', 'email',
                  'is_active', 'date_joined')


class RecordSerializer(serializers.ModelSerializer):
    '''Indicate how to serialize Record instance.'''
    class Meta:
        model = training_record.models.Record
        fields = '__all__'


class RecordContentSerializer(serializers.ModelSerializer):
    '''Indicate how to serialize RecordContent instance.'''
    class Meta:
        model = training_record.models.RecordContent
        fields = '__all__'


class RecordAttachmentSerializer(serializers.ModelSerializer):
    '''Indicate how to serialize RecordAttachment instance.'''
    class Meta:
        model = training_record.models.RecordAttachment
        fields = '__all__'


class StatusChangeLogSerializer(serializers.ModelSerializer):
    '''Indicate how to serialize StatusChangeLog instance.'''
    class Meta:
        model = training_record.models.StatusChangeLog
        fields = '__all__'       