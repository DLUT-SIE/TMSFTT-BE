'''Define how to serialize our models.'''
from rest_framework import serializers
from rest_framework_bulk import (
    BulkListSerializer,
    BulkSerializerMixin,
)

import training_record.models as record_models
from training_record.services import RecordService
from training_event.serializers import (
    CampusEventSerializer, OffCampusEventSerializer
)


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


class RecordSerializer(serializers.ModelSerializer):
    '''Indicate how to serialize Record instance.'''
    # Write-Only fields
    off_campus_event_data = serializers.JSONField(binary=True, write_only=True)
    contents_data = serializers.ListField(
        child=serializers.JSONField(binary=True),
        write_only=True,
        required=False,
    )
    attachments_data = serializers.ListField(
        child=serializers.FileField(),
        write_only=True,
        required=False,
    )

    # Read-Only fields
    campus_event = CampusEventSerializer(read_only=True)
    off_campus_event = OffCampusEventSerializer(read_only=True)
    attachments = RecordAttachmentSerializer(many=True, read_only=True)
    contents = RecordContentSerializer(many=True, read_only=True)

    class Meta:
        model = record_models.Record
        fields = '__all__'

    def create(self, validated_data):
        return RecordService.create_off_campus_record_from_raw_data(
            **validated_data)


class StatusChangeLogSerializer(serializers.ModelSerializer):
    '''Indicate how to serialize StatusChangeLog instance.'''
    class Meta:
        model = record_models.StatusChangeLog
        fields = '__all__'
