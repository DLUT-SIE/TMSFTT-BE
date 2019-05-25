'''Define how to serialize our models.'''
from rest_framework import serializers
from django.utils.timezone import now
import training_event.models
from training_event.services import EnrollmentService, CampusEventService, CoefficientService
from training_program.serializers import ReadOnlyProgramSerializer


class CampusEventSerializer(serializers.ModelSerializer):
    '''Indicate how to serialize Campus Event instance for reading.'''
    expired = serializers.SerializerMethodField(read_only=True)
    enrolled = serializers.SerializerMethodField(read_only=True)
    program_detail = ReadOnlyProgramSerializer(source='program',
                                               read_only=True)
    enrollment_id = serializers.SerializerMethodField(read_only=True)
    coefficients_detail = serializers.SerializerMethodField(read_only=True)
    #给前端用，一个是修改表单的时候需要读取数据，另外是页面详情展示培训活动系数

    class Meta:
        model = training_event.models.CampusEvent
        fields = '__all__'
        # read_only_fields = ('num_enrolled', 'reviewed')
    
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
    
    def get_coefficients_detail(self, obj):
        '''Get event enrollments id.'''
        key = 'coefficients_detail_cache'
        user = self.context['request'].user
        if key not in self.context:
            if not isinstance(self.instance, list):
                instances = [self.instance]

            else:
                instances = self.instance
            res = CoefficientService.get_coefficients_detail(
                instances
            )
            self.context[key] = res
        else:
            res = self.context[key]
        return res.get(obj.id, None)

class CampusEventCreateSerializer(serializers.ModelSerializer):
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

    def create(self, validated_data):
        '''Create event and event coefficient.'''
        print("create")
        coefficients = validated_data.pop('coefficients')
        return CampusEventService.create_campus_event(
            validated_data, coefficients, self.context)
            
    def update(self, instance, validated_data):
        coefficient = validated_data.pop('coefficients')
        print("update")
        event_id = instance.id
        CoefficientService.update_coefficient(event_id, coefficient)
        return CampusEventService.update_campus_event(instance, validated_data,
                                             self.context)

'''
class CampusEventSerializer(serializers.ModelSerializer):
    Indicate how to serialize CampusEvent instance.
    expired = serializers.SerializerMethodField(read_only=True)
    enrolled = serializers.SerializerMethodField(read_only=True)
    program_detail = ReadOnlyProgramSerializer(source='program',
                                               read_only=True)
    enrollment_id = serializers.SerializerMethodField(read_only=True)
    coefficients = serializers.ListField(s
        write_only=True, child=serializers.JSONField())
    
    # coefficients_detail = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = training_event.models.CampusEvent
        fields = '__all__'
        read_only_fields = ('num_enrolled', 'reviewed')

    def get_expired(self, obj):
        Get event expired status.
        return now() > obj.deadline or obj.num_enrolled >= obj.num_participants

    def get_enrolled(self, obj):
        Get event enrollments status.
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
        Get event enrollments id.
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

    def validate_coefficients(self, data):
        Forbid non-school-admins to update reviewed coefficients.
        if (self.instance  # Update an object
                and self.instance.reviewed  # Has been reviewed by school admin
                and not self.context['request'].user.is_school_admin):
            raise serializers.ValidationError(
                '非校管理员无权修改已经审核通过的培训系数')
        return data

    def create(self, validated_data):
        Create event and event coefficient.
        coefficients = validated_data.pop('coefficients')
        return CampusEventService.create_campus_event(
            validated_data, coefficients, self.context)
            
    def update(self, instance, validated_data):
        coefficient = validated_data.pop('coefficients')
        # print(coefficient)
        event_id = instance.id
        a = training_event.models.EventCoefficient.objects.filter(
            campus_event = event_id, role=1
        )
        print(type(a))
        # CoefficientService.update_coefficient(event.id, coefficient)
        return CampusEventService.update_campus_event(instance, validated_data,
                                             self.context)
    def get_coefficients_detail(self, obj):
        Get event enrollments id.
        key = 'coefficients_detail_cache'
        user = self.context['request'].user
        if key not in self.context:
            if not isinstance(self.instance, list):
                instances = [self.instance]
            else:
                instances = self.instance
            res = CoefficientService.get_coefficients_detail(
                instances
            )
            self.context[key] = res
        else:
            res = self.context[key]
        return res.get(obj.id, None)
'''


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
