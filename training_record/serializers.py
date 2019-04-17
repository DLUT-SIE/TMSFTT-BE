'''Define how to serialize our models.'''
from rest_framework import serializers
from rest_framework_bulk import (
    BulkListSerializer,
    BulkSerializerMixin,
)

from infra.utils import format_file_size
from training_record.models import (
    Record,
    RecordAttachment,
    RecordContent,
    StatusChangeLog,
    CampusEventFeedback,
)
from training_record.services import RecordService, CampusEventFeedbackService
from training_event.serializers import (
    CampusEventSerializer, OffCampusEventSerializer
)


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


class CampusEventFeedbackSerializer(serializers.ModelSerializer):
    '''Indicate how to serialize CampusEventFeedback instance.'''
    class Meta:
        model = CampusEventFeedback
        fields = '__all__'

    def create(self, validated_data):
        return CampusEventFeedbackService.create_feedback(
            **validated_data)


class RecordSerializer(serializers.ModelSerializer):
    '''Indicate how to serialize Record instance.'''
    # Write-Only fields
    off_campus_event_data = serializers.JSONField(binary=True, write_only=True)
    contents_data = serializers.ListField(
        child=serializers.JSONField(binary=True),
        write_only=True,
        default=lambda: [],
    )
    attachments_data = serializers.ListField(
        child=serializers.FileField(),
        write_only=True,
        default=lambda: [],
    )

    # Read-Only fields
    status_str = serializers.CharField(source='get_status_display',
                                       read_only=True)
    campus_event = CampusEventSerializer(read_only=True)
    off_campus_event = OffCampusEventSerializer(read_only=True)
    attachments = RecordAttachmentSerializer(many=True, read_only=True)
    contents = RecordContentSerializer(many=True, read_only=True)
    feedback = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = Record
        fields = ('id', 'create_time', 'update_time', 'campus_event',
                  'off_campus_event', 'off_campus_event_data',
                  'user', 'status', 'contents', 'contents_data',
                  'attachments', 'attachments_data',
                  'status_str', 'feedback')

    def create(self, validated_data):
        return RecordService.create_off_campus_record_from_raw_data(
            **validated_data)

    def validate_attachments_data(self, data):  # pylint: disable=no-self-use
        '''Validate attachments data.'''
        # TODO(youchen): Use global configs
        if len(data) > 3:
            raise serializers.ValidationError('最多允许上传3个附件')
        size_bytes = sum(x.size for x in data)
        # TODO(youchen): Use global configs
        if size_bytes > 10 * 1024 * 1024:  # 10 MB
            raise serializers.ValidationError(
                '上传附件过大，请修改后再上传。(附件大小: {})'.format(
                    format_file_size(size_bytes)))
        return data


class StatusChangeLogSerializer(serializers.ModelSerializer):
    '''Indicate how to serialize StatusChangeLog instance.'''
    class Meta:
        model = StatusChangeLog
        fields = '__all__'
