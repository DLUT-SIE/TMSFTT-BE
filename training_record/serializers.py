'''Define how to serialize our models.'''
import os.path as osp

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
from secure_file.fields import SecureFileField
from training_event.models import EventCoefficient
from training_event.serializers import (
    BasicReadOnlyCampusEventSerializer, OffCampusEventSerializer
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
    path = SecureFileField(perm_name='view_recordattachment')

    class Meta:
        model = RecordAttachment
        fields = '__all__'
        list_serializer_class = BulkListSerializer


class CampusEventFeedbackSerializer(serializers.ModelSerializer):
    '''Indicate how to serialize CampusEventFeedback instance.'''
    class Meta:
        model = CampusEventFeedback
        fields = ('id', 'create_time', 'record', 'content')

    def create(self, validated_data):
        return CampusEventFeedbackService.create_feedback(
            **validated_data)


class ReadOnlyRecordSerializer(serializers.ModelSerializer):
    '''Indicate how to serialize Record instance for reading.'''
    status_str = serializers.CharField(source='get_status_display',
                                       read_only=True)
    role_str = serializers.CharField(
        source='event_coefficient.get_role_display',
        read_only=True)
    role = serializers.IntegerField(
        source='event_coefficient.role',
        read_only=True)
    allow_actions_from_user = (
        serializers.SerializerMethodField(read_only=True))
    allow_actions_from_department_admin = (
        serializers.SerializerMethodField(read_only=True))
    allow_actions_from_school_admin = (
        serializers.SerializerMethodField(read_only=True))
    off_campus_event = OffCampusEventSerializer(read_only=True)
    campus_event = BasicReadOnlyCampusEventSerializer(read_only=True)

    class Meta:
        model = Record
        fields = ('id', 'create_time', 'update_time', 'campus_event',
                  'off_campus_event', 'user', 'status', 'contents',
                  'attachments', 'status_str', 'feedback', 'role', 'role_str',
                  'allow_actions_from_user',
                  'allow_actions_from_department_admin',
                  'allow_actions_from_school_admin')

    def get_allow_actions_from_user(self, obj):
        '''Get status of whether ordinary user can edit record or not.'''
        allow_user_action_status = (
            Record.STATUS_SUBMITTED,
            Record.STATUS_DEPARTMENT_ADMIN_REJECTED,
            Record.STATUS_SCHOOL_ADMIN_REJECTED
        )
        return obj.status in allow_user_action_status

    def get_allow_actions_from_department_admin(self, obj):
        '''Get status of whether department admin can review or not.'''
        allow_department_action_status = (
            Record.STATUS_SUBMITTED,
            Record.STATUS_DEPARTMENT_ADMIN_APPROVED,
            Record.STATUS_DEPARTMENT_ADMIN_REJECTED
        )
        return obj.status in allow_department_action_status

    def get_allow_actions_from_school_admin(self, obj):
        '''Get status of whether school admin can review or not.'''
        allow_school_action_status = (
            Record.STATUS_DEPARTMENT_ADMIN_APPROVED,
            Record.STATUS_SCHOOL_ADMIN_APPROVED,
            Record.STATUS_SCHOOL_ADMIN_REJECTED,
        )
        return obj.status in allow_school_action_status


class RecordCreateSerializer(serializers.ModelSerializer):
    '''Indicate how to serialize Record instance.'''
    off_campus_event = serializers.JSONField(
        binary=True,
        write_only=True,
        required=True,
    )
    contents = serializers.ListField(
        child=serializers.JSONField(binary=True),
        write_only=True,
        required=False,
    )
    attachments = serializers.ListField(
        child=serializers.FileField(),
        write_only=True,
        required=False,
    )
    feedback = serializers.PrimaryKeyRelatedField(read_only=True)
    role = serializers.ChoiceField(
        choices=EventCoefficient.ROLE_CHOICES,
        write_only=True,
        default=EventCoefficient.ROLE_PARTICIPATOR,
    )

    class Meta:
        model = Record
        fields = ('id', 'create_time', 'update_time', 'campus_event',
                  'off_campus_event', 'user', 'status', 'contents',
                  'attachments', 'feedback', 'role')

    def create(self, validated_data):
        return RecordService.create_off_campus_record_from_raw_data(
            **validated_data)

    def update(self, instance, validated_data):
        return RecordService.update_off_campus_record_from_raw_data(
            instance, **validated_data)

    def validate_attachments(self, data):
        '''Validate attachments data.'''
        max_count = 3
        max_size = 10 * 1024 * 1024  # 10 MB
        if self.instance:
            max_count -= len(self.instance.attachments.all())
            max_size -= sum(x.path.size
                            for x in self.instance.attachments.all())
        valid_extensions = {'.pdf', '.png', '.jpg', '.jpeg', '.doc', '.docx'}
        for inmemory_file in data:
            ext = osp.splitext(inmemory_file.name)[-1].lower()
            if ext not in valid_extensions:
                raise serializers.ValidationError(
                    f'不被支持的文件类型: {inmemory_file.name}')
        # TODO(youchen): Use global configs
        if len(data) > max_count:
            raise serializers.ValidationError('最多允许上传3个附件')
        size_bytes = sum(x.size for x in data)
        # TODO(youchen): Use global configs
        if size_bytes > max_size:
            raise serializers.ValidationError(
                '上传附件过大，请修改后再上传。(附件大小: {})'.format(
                    format_file_size(size_bytes)))
        return data


class StatusChangeLogSerializer(serializers.ModelSerializer):
    '''Indicate how to serialize StatusChangeLog instance.'''
    class Meta:
        model = StatusChangeLog
        fields = '__all__'
