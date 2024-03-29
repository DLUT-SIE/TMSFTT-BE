'''Define how to serialize our models.'''
import smtplib

from django.utils.timezone import now
from django.contrib.auth import get_user_model
from django.core.mail import send_mass_mail
from rest_framework import serializers

import training_event.models
from training_event.services import EnrollmentService, CampusEventService
from infra.mixins import HumanReadableValidationErrorMixin
from infra.utils import prod_logger
from infra.services import NotificationService, SOAPSMSService
from training_program.serializers import ReadOnlyProgramSerializer

User = get_user_model()


class EventCoefficientSerializer(HumanReadableValidationErrorMixin,
                                 serializers.ModelSerializer):
    '''Indicate how to serialize EventCoefficient instance.'''
    hours_option_str = serializers.CharField(
        source='get_hours_option_display',
        read_only=True)
    workload_option_str = serializers.CharField(
        source='get_workload_option_display',
        read_only=True)
    role_str = serializers.CharField(
        source='get_role_display',
        read_only=True)

    class Meta:
        model = training_event.models.EventCoefficient
        fields = ('campus_event', 'off_campus_event', 'role',
                  'coefficient', 'hours_option', 'workload_option',
                  'hours_option_str', 'workload_option_str', 'role_str')


class ReadOnlyCampusEventSerializer(HumanReadableValidationErrorMixin,
                                    serializers.ModelSerializer):
    '''Indicate how to serialize Campus Event instance for reading.'''
    expired = serializers.SerializerMethodField(read_only=True)
    enrolled = serializers.SerializerMethodField(read_only=True)
    program_detail = ReadOnlyProgramSerializer(
        source='program', read_only=True)
    enrollment_id = serializers.SerializerMethodField(read_only=True)
    coefficients = EventCoefficientSerializer(
        read_only=True, many=True)

    class Meta:
        model = training_event.models.CampusEvent
        fields = ('id', 'name', 'time', 'location', 'create_time',
                  'update_time', 'reviewed', 'expired', 'enrolled',
                  'enrollment_id', 'num_hours', 'num_enrolled',
                  'num_participants', 'program', 'program_detail',
                  'coefficients', 'deadline', 'description')

    def get_expired(self, obj):
        '''Get event expired status.'''
        return now() > obj.deadline or obj.num_enrolled >= obj.num_participants

    def get_enrolled(self, obj):
        '''Get event enrollments status.'''
        key = 'enrolled_cache'
        user = self.context['request'].user
        if key not in self.context:
            if not isinstance(self.instance, list):
                instances = [self.instance]
            else:
                instances = self.instance
            res = EnrollmentService.get_user_enrollment_status(
                instances, user
            )
            self.context[key] = res
        else:
            res = self.context[key]
        return res.get(obj.id, None)

    def get_enrollment_id(self, obj):
        '''Get event enrollments id.'''
        key = 'enrollment_cache'
        user = self.context['request'].user
        if key not in self.context:
            if not isinstance(self.instance, list):
                instances = [self.instance]
            else:
                instances = self.instance
            res = EnrollmentService.get_user_enrollment_id(
                instances, user
            )
            self.context[key] = res
        else:
            res = self.context[key]
        return res.get(obj.id, None)


class BasicReadOnlyCampusEventSerializer(ReadOnlyCampusEventSerializer):
    '''Serialize basic information for campus event.'''
    class Meta(ReadOnlyCampusEventSerializer.Meta):
        fields = ('id', 'name', 'time', 'location', 'create_time',
                  'update_time', 'enrollment_id', 'num_hours', 'num_enrolled',
                  'num_participants', 'program_detail',
                  'deadline', 'description')


class CampusEventSerializer(HumanReadableValidationErrorMixin,
                            serializers.ModelSerializer):
    '''Indicate how to serializer Campus Event instance.'''
    coefficients = serializers.ListField(
        write_only=True, child=serializers.JSONField())

    class Meta:
        model = training_event.models.CampusEvent
        fields = '__all__'
        read_only_fields = ('num_enrolled', 'reviewed')

    def validate_coefficients(self, data):
        '''Forbid non-school-admins to update reviewed coefficients.'''
        if (self.instance  # Update an object
                and self.instance.reviewed  # Has been reviewed by school admin
                and not self.context['request'].user.is_school_admin):
            raise serializers.ValidationError(
                '非校管理员无权修改已经审核通过的培训系数')
        return data

    def validate(self, data):
        '''Forbid update event if reviewed is true.'''
        if (self.instance
                and self.instance.reviewed
                and not self.context['request'].user.is_school_admin):
            raise serializers.ValidationError(
                '活动已被学校管理员审核，不可修改')
        return data

    def validate_program(self, program):
        '''Forbid update and create event if program is wrong.'''
        if self.instance and self.instance.program != program:
            raise serializers.ValidationError("你无权修改培训活动！")
        if not self.context['request'].user.has_perm(
                'training_program.change_program', program):
            raise serializers.ValidationError('您无权创建培训活动！')
        return program

    def create(self, validated_data):
        '''Create event and event coefficient.'''
        coefficients = validated_data.pop('coefficients')
        if self.context['request'].user.is_school_admin:
            validated_data['reviewed'] = True
        else:
            school_admin = User.objects.get(id=10977)
            mails = []
            smses = []
            msg = (
                '有新的培训活动需要审核'
            )

            mail = (
                '培训活动审核提醒',
                msg,
                'TMSFTT',
                [school_admin.email],
            )
            mails.append(mail)

            sms = {
                'user_phone_number': school_admin.cell_phone_number,
                'sms_info': msg,
            }
            smses.append(sms)

            NotificationService.send_system_notification(school_admin, msg)

            try:
                send_mass_mail(mails, fail_silently=False)
            except smtplib.SMTPException as exc:
                msg = (
                    '系统在提醒管理员审批活动时发生错误，'
                    f'邮件可能未成功发送，错误信息为：{exc}'
                )
                prod_logger.error(msg)

            try:
                SOAPSMSService.send_sms(smses)
            except Exception as exc:
                msg = (
                    '系统在提醒管理员审批活动时发生错误，'
                    f'短信可能未成功发送，错误信息为：{exc}'
                )
                prod_logger.error(msg)

        return CampusEventService.create_campus_event(
            validated_data, coefficients, self.context)

    def update(self, instance, validated_data):
        '''Update event and event coefficient.'''
        coefficients = validated_data.pop('coefficients', [])
        return CampusEventService.update_campus_event(instance,
                                                      validated_data,
                                                      coefficients,
                                                      self.context)


class OffCampusEventSerializer(HumanReadableValidationErrorMixin,
                               serializers.ModelSerializer):
    '''Indicate how to serialize OffCampusEvent instance.'''
    class Meta:
        model = training_event.models.OffCampusEvent
        fields = '__all__'


class EnrollmentSerailizer(HumanReadableValidationErrorMixin,
                           serializers.ModelSerializer):
    '''Indicate how to serialize Enrollment instance.'''
    user = serializers.PrimaryKeyRelatedField(allow_null=True,
                                              read_only=True)

    class Meta:
        model = training_event.models.Enrollment
        fields = '__all__'

    def create(self, validated_data):
        return EnrollmentService.create_enrollment(validated_data)

    def validate(self, data):
        current_user = self.context['request'].user
        request_data = self.context['request'].data
        if 'user' not in request_data:
            data['user'] = current_user
        else:
            user_id = request_data['user']
            user = User.objects.get(pk=user_id)
            if not current_user.is_school_admin:
                raise serializers.ValidationError(
                    '您没有权限为用户报名该活动')
            data['user'] = user
        if not data['campus_event'].reviewed:
            raise serializers.ValidationError('不能报名未经审核的培训活动')
        existance = (
            training_event.models.Enrollment.objects
            .filter(user=data['user'], campus_event=data['campus_event'])
            .exists()
        )
        if existance:
            raise serializers.ValidationError('您已报名，请勿重复报名')
        return data


class EnrollmentReadOnlySerailizer(HumanReadableValidationErrorMixin,
                                   serializers.ModelSerializer):
    '''To serializer enrollment instance.'''
    user = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = training_event.models.Enrollment
        fields = '__all__'

    def get_user(self, obj):
        '''Serialize necessary information about user.'''
        user = obj.user
        return {
            'department_str': user.department.name,
            'username': user.username,
            'first_name': user.first_name,
            'cell_phone_number': user.cell_phone_number,
            'email': user.email,
            'technical_title': user.technical_title,
        }
