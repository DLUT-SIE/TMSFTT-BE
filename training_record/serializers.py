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
    status_str = serializers.SerializerMethodField()
    campus_event = CampusEventSerializer(read_only=True)
    off_campus_event = OffCampusEventSerializer(read_only=True)
    attachments = RecordAttachmentSerializer(many=True, read_only=True)
    contents = RecordContentSerializer(many=True, read_only=True)

    class Meta:
        model = Record
        fields = '__all__'

    def get_status_str(self, obj):  # pylint: disable=no-self-use
        '''Return status represented by Chinese chars.'''
        status = obj.status
        status_char = ''
        if status == 0:
            status_char = '未提交'
        elif status == 1:
            status_char = '已提交'
        elif status == 2:
            status_char = '院系管理员已审核'
        elif status == 3:
            status_char = '学校管理员已审核'
        else:
            status_char = '未知状态'
        return status_char

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
