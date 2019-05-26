'''Define how to serialize our models.'''
from rest_framework import serializers
from django.utils.timezone import now
import training_event.models
from training_event.services import EnrollmentService, CampusEventService
from training_program.serializers import ReadOnlyProgramSerializer


class EventCoefficientSerializer(serializers.ModelSerializer):
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


class ReadOnlyCampusEventSerializer(serializers.ModelSerializer):
    '''Indicate how to serialize Campus Event instance for reading.'''
    expired = serializers.SerializerMethodField(read_only=True)
    enrolled = serializers.SerializerMethodField(read_only=True)
    program_detail = ReadOnlyProgramSerializer(source='program',
                                               read_only=True)
    enrollment_id = serializers.SerializerMethodField(read_only=True)
    coefficients = EventCoefficientSerializer(source='eventcoefficient_set',
                                              read_only=True,
                                              many=True)

    class Meta:
        model = training_event.models.CampusEvent
        fields = ('id', 'name', 'time', 'location', 'create_time',
                  'update_time', 'reviewed', 'expired', 'enrolled',
                  'enrollment_id', 'num_hours', 'num_participants',
                  'program', 'program_detail', 'coefficients',
                  'deadline', 'description')

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


class CampusEventSerializer(serializers.ModelSerializer):
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

    def validate_reviewed(self, data):
        '''Forbid update event if reviewed is true.'''
        if (self.instance and self.instance.reviewed):
            raise serializers.ValidationError(
                '活动已被学校管理员审核，不可修改')
        return data

    def create(self, validated_data):
        '''Create event and event coefficient.'''
        coefficients = validated_data.pop('coefficients')
        return CampusEventService.create_campus_event(
            validated_data, coefficients, self.context)

    def update(self, instance, validated_data):
        '''Update event and event coefficient.'''
        coefficients = validated_data.pop('coefficients')
        return CampusEventService.update_campus_event(instance,
                                                      validated_data,
                                                      coefficients,
                                                      self.context)


class OffCampusEventSerializer(serializers.ModelSerializer):
    '''Indicate how to serialize OffCampusEvent instance.'''
    class Meta:
        model = training_event.models.OffCampusEvent
        fields = '__all__'


class EnrollmentSerailizer(serializers.ModelSerializer):
    '''Indicate how to serialize Enrollment instance.'''
    user = serializers.PrimaryKeyRelatedField(allow_null=True,
                                              read_only=True)

    class Meta:
        model = training_event.models.Enrollment
        fields = '__all__'

    def create(self, validated_data):
        if 'user' not in validated_data and 'request' in self.context:
            validated_data['user'] = self.context['request'].user
        return EnrollmentService.create_enrollment(validated_data)
