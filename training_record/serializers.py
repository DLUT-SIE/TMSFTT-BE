'''Define how to serialize our models.'''
import os.path as osp

from rest_framework import serializers
from rest_framework_bulk import (
    BulkListSerializer,
    BulkSerializerMixin,
)

from infra.utils import format_file_size
from infra.mixins import HumanReadableValidationErrorMixin
from training_record.models import (
    Record,
    RecordAttachment,
    RecordContent,
    StatusChangeLog,
    CampusEventFeedback,
)
from training_record.utils import (
    is_user_allowed_operating,
    is_admin_allowed_operating,
)
from training_record.services import RecordService, CampusEventFeedbackService
from secure_file.fields import SecureFileField
from training_event.models import EventCoefficient
from training_event.serializers import (
    BasicReadOnlyCampusEventSerializer, OffCampusEventSerializer
)


class RecordContentSerializer(BulkSerializerMixin,
                              HumanReadableValidationErrorMixin,
                              serializers.ModelSerializer):
    '''Indicate how to serialize RecordContent instance.'''
    class Meta:
        model = RecordContent
        fields = '__all__'
        list_serializer_class = BulkListSerializer


class RecordAttachmentSerializer(BulkSerializerMixin,
                                 HumanReadableValidationErrorMixin,
                                 serializers.ModelSerializer):
    '''Indicate how to serialize RecordAttachment instance.'''
    path = SecureFileField(perm_name='view_recordattachment')

    class Meta:
        model = RecordAttachment
        fields = '__all__'
        list_serializer_class = BulkListSerializer


class CampusEventFeedbackSerializer(HumanReadableValidationErrorMixin,
                                    serializers.ModelSerializer):
    '''Indicate how to serialize CampusEventFeedback instance.'''
    class Meta:
        model = CampusEventFeedback
        fields = ('id', 'create_time', 'record', 'content')

    def create(self, validated_data):
        return CampusEventFeedbackService.create_feedback(
            **validated_data, context=self.context)

    def validate(self, data):
        record = data.get('record')
        if not self.context['request'].user.has_perm(
                'training_record.change_record', record):
            raise serializers.ValidationError('您没有权限为此记录提交反馈')
        return data


class ReadOnlyRecordSerializer(HumanReadableValidationErrorMixin,
                               serializers.ModelSerializer):
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
    allow_actions_from_admin = (
        serializers.SerializerMethodField(read_only=True))
    off_campus_event = OffCampusEventSerializer(read_only=True)
    campus_event = BasicReadOnlyCampusEventSerializer(read_only=True)

    class Meta:
        model = Record
        fields = ('id', 'create_time', 'update_time', 'campus_event',
                  'off_campus_event', 'user', 'status', 'contents',
                  'attachments', 'status_str', 'feedback', 'role', 'role_str',
                  'allow_actions_from_user', 'allow_actions_from_admin')

    def get_allow_actions_from_user(self, obj):
        '''Get status of whether ordinary user can edit record or not.'''
        return is_user_allowed_operating(self.context['request'], obj)

    def get_allow_actions_from_admin(self, obj):
        '''Get status of whether department admin can review or not.'''
        return is_admin_allowed_operating(self.context['request'], obj)


class RecordWriteSerializer(HumanReadableValidationErrorMixin,
                            serializers.ModelSerializer):
    '''Indicate how to serialize Record instance.'''
    off_campus_event = serializers.JSONField(
        binary=True,
        write_only=True,
        required=True,
        label='校外培训活动',
    )
    contents = serializers.ListField(
        child=serializers.JSONField(binary=True),
        write_only=True,
        required=False,
        label='培训记录内容',
    )
    attachments = serializers.ListField(
        child=serializers.FileField(),
        write_only=True,
        required=False,
        label='培训记录附件',
    )
    feedback = serializers.PrimaryKeyRelatedField(read_only=True)
    role = serializers.ChoiceField(
        choices=EventCoefficient.ROLE_CHOICES,
        write_only=True,
        default=EventCoefficient.ROLE_PARTICIPATOR,
        label='角色身份',
    )

    class Meta:
        model = Record
        fields = ('id', 'create_time', 'update_time', 'campus_event',
                  'off_campus_event', 'user', 'status', 'contents',
                  'attachments', 'feedback', 'role')

    def validate_off_campus_event(self, data):
        '''Use serializer to validate off_campus_event.'''
        off_campus_event_serializer = OffCampusEventSerializer(data=data)
        off_campus_event_serializer.is_valid(raise_exception=True)
        return off_campus_event_serializer.validated_data

    def create(self, validated_data):
        return RecordService.create_off_campus_record_from_raw_data(
            validated_data)

    def update(self, instance, validated_data):
        return RecordService.update_off_campus_record_from_raw_data(
            instance, validated_data, self.context)

    def validate(self, data):
        '''Ensure having rights to update records'''
        if not self.instance:
            data['user'] = self.context['request'].user
            return data

        data['user'] = self.instance.user
        if (is_user_allowed_operating(self.context['request'], self.instance)
                or is_admin_allowed_operating(
                    self.context['request'], self.instance)):
            return data
        raise serializers.ValidationError('在此状态下您无法更改')

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


class StatusChangeLogSerializer(HumanReadableValidationErrorMixin,
                                serializers.ModelSerializer):
    '''Indicate how to serialize StatusChangeLog instance.'''
    pre_status_str = serializers.CharField(source='get_pre_status_display')
    post_status_str = serializers.CharField(source='get_post_status_display')
    user = serializers.CharField(source='user.first_name')

    class Meta:
        model = StatusChangeLog
        fields = '__all__'
