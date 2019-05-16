'''Define how to serialize our models.'''
from rest_framework import serializers
from django.utils.timezone import now
import training_event.models
from training_event.services import EnrollmentService
from training_program.serializers import ReadOnlyProgramSerializer


class CampusEventSerializer(serializers.ModelSerializer):
    '''Indicate how to serialize CampusEvent instance.'''
    expired = serializers.SerializerMethodField(read_only=True)
    enrolled = serializers.SerializerMethodField(read_only=True)
    program_detail = ReadOnlyProgramSerializer(source='program',
                                               read_only=True)
    enrollment_id = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = training_event.models.CampusEvent
        fields = '__all__'
        read_only_fields = ('num_enrolled',)

    def get_expired(self, obj):
        '''Get event expired status.'''
        return now() > obj.deadline

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
        return res[obj.id]

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
        return res[obj.id]


class OffCampusEventSerializer(serializers.ModelSerializer):
    '''Indicate how to serialize OffCampusEvent instance.'''
    class Meta:
        model = training_event.models.OffCampusEvent
        fields = '__all__'


class EnrollmentSerailizer(serializers.ModelSerializer):
    '''Indicate how to serialize Enrollment instance.'''
    class Meta:
        model = training_event.models.Enrollment
        fields = '__all__'
        read_only_fields = ('is_participated', 'user')

    def create(self, validated_data):
        return EnrollmentService.create_enrollment(validated_data,
                                                   self.context)
