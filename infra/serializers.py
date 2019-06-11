'''Define how to serialize our models.'''
from rest_framework import serializers

import infra.models
from infra.mixins import HumanReadableValidationErrorMixin


class NotificationSerializer(HumanReadableValidationErrorMixin,
                             serializers.ModelSerializer):
    '''Indicate how to serialize Notification instance.'''
    sender = serializers.SlugRelatedField(
        read_only=True, slug_field='first_name'
    )
    recipient = serializers.SlugRelatedField(
        read_only=True, slug_field='first_name'
    )

    class Meta:
        model = infra.models.Notification
        fields = '__all__'
