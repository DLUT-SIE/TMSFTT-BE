'''Define how to serialize our models.'''
from rest_framework import serializers

from infra.mixins import HumanReadableValidationErrorMixin
from auth.models import Department
from training_program.models import Program
from training_program.services import ProgramService


class ProgramSerializer(HumanReadableValidationErrorMixin,
                        serializers.ModelSerializer):
    '''Indicate how to serialize Program instance.'''

    class Meta:
        model = Program
        fields = '__all__'

    def create(self, validated_data):
        return ProgramService.create_program(validated_data, self.context)

    def update(self, instance, validated_data):
        return ProgramService.update_program(instance, validated_data,
                                             self.context)

    def validate_department(self, department):
        '''Forbid illegal create of department.'''
        if self.instance is not None:
            if department.id != self.instance.department.id:
                raise serializers.ValidationError('不可以修改培训项目的院系')
        if self.instance is None:
            if self.context['request'].user.is_school_admin:
                department = Department.objects.get(name='大连理工大学')
            elif not self.context['request'].user.check_department_admin(
                    department):
                raise serializers.ValidationError('无效的院系')
        return department


class ReadOnlyProgramSerializer(serializers.ModelSerializer):
    '''Indicate how to serialize read_only Program instance.'''
    category_str = serializers.CharField(source='get_category_display',
                                         read_only=True)
    department = serializers.SlugField(read_only=True,
                                       source='department.name')

    class Meta:
        model = Program
        fields = '__all__'
