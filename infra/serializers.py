'''Define how to serialize our models.'''
from rest_framework import serializers

import infra.models


class NotificationSerializer(serializers.ModelSerializer):
    '''Indicate how to serialize Notification instance.'''
    sender = serializers.SlugRelatedField(slug_field='first_name',
                                          read_only=True)
    recipient = serializers.SlugRelatedField(slug_field='first_name',
                                             read_only=True)

    class Meta:
        model = infra.models.Notification
        fields = '__all__'
