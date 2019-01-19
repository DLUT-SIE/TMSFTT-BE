'''Define how to serialize our models.'''
from rest_framework import serializers
from rest_framework_bulk import (
    BulkListSerializer,
    BulkSerializerMixin,
)

import training_record.models as record_models
from training_record.utils import (
    infer_attachment_type,
)


class RecordSerializer(serializers.ModelSerializer):
    '''Indicate how to serialize Record instance.'''
    class Meta:
        model = record_models.Record
        fields = '__all__'


class RecordContentSerializer(BulkSerializerMixin,
                              serializers.ModelSerializer):
    '''Indicate how to serialize RecordContent instance.'''
    class Meta:
        model = record_models.RecordContent
        fields = '__all__'
        list_serializer_class = BulkListSerializer


class RecordAttachmentSerializer(BulkSerializerMixin,
                                 serializers.ModelSerializer):
    '''Indicate how to serialize RecordAttachment instance.'''
    class Meta:
        model = record_models.RecordAttachment
        fields = '__all__'
        list_serializer_class = BulkListSerializer

    def validate(self, attrs):
        '''Object-level validation.'''
        if 'attachment_type' not in attrs:
            # Infer attachment_type
            attrs['attachment_type'] = infer_attachment_type(
                attrs['path'].name)
        return super().validate(attrs)


class StatusChangeLogSerializer(serializers.ModelSerializer):
    '''Indicate how to serialize StatusChangeLog instance.'''
    class Meta:
        model = record_models.StatusChangeLog
        fields = '__all__'
