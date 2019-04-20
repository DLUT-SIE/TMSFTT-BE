'''Define how to serialize our models.'''
from rest_framework import serializers
from rest_framework_bulk import (
    BulkListSerializer,
    BulkSerializerMixin,
)

from infra.utils import format_file_size
from training_record.models import (
    Record, RecordAttachment, RecordContent, StatusChangeLog
)
from training_record.services import RecordService


class RecordContentSerializer(BulkSerializerMixin,
                              serializers.ModelSerializer):
    '''Indicate how to serialize RecordContent instance.'''
    class Meta:
        model = RecordContent
        fields = '__all__'
        list_serializer_class = BulkListSerializer


class RecordAttachmentSerializer(BulkSerializerMixin,
                                 serializers.ModelSerializer):
    '''Indicate how to serialize RecordAttachment instance.'''
    class Meta:
        model = RecordAttachment
        fields = '__all__'
        list_serializer_class = BulkListSerializer

    def validate_path(self, data):  # pylint: disable=no-self-use
        '''Validate the file in attachments.'''
        # TODO(youchen): Use global configs
        if data.size > 10 * 1024 * 1024:  # 10 MB
            raise serializers.ValidationError(
                '上传附件过大，请修改后再上传。(附件大小: {})'.format(
                    format_file_size(data.size)))
        return data


class RecordSerializer(serializers.ModelSerializer):
    '''Indicate how to serialize Record instance.'''

    # Read-Only fields
    status_str = serializers.CharField(source='get_status_display',
                                       read_only=True)

    class Meta:
        model = Record
        fields = ('user', 'id', 'status_str', 'campus_event',
                  'off_campus_event', 'contents', 'attachments',
                  'status', 'update_time', 'create_time')

    def create(self, validated_data):
        return RecordService.create_off_campus_record_from_raw_data(
            **validated_data)

    def validate_attachments(self, data):  # pylint: disable=no-self-use
        '''Validate attachments data.'''
        # TODO(youchen): Use global configs
        if len(data) > 3:
            raise serializers.ValidationError('最多允许上传3个附件')
        return data


class StatusChangeLogSerializer(serializers.ModelSerializer):
    '''Indicate how to serialize StatusChangeLog instance.'''
    class Meta:
        model = StatusChangeLog
        fields = '__all__'
