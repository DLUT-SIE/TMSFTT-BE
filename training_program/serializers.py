'''Define how to serialize our models.'''
from rest_framework import serializers

from training_program.models import Program
from training_program.services import ProgramService


class ProgramSerializer(serializers.ModelSerializer):
    '''Indicate how to serialize Program instance.'''

    class Meta:
        model = Program
        fields = '__all__'

    def create(self, validated_data):
        return ProgramService.create_program(validated_data, self.context)

    def update(self, instance, validated_data):
<<<<<<< a8854aeb335613c4011d054f5d8569afa55b9d5d
        return ProgramService.update_program(instance, validated_data,
                                             self.context)
=======
        validated_data.pop('department')
        return ProgramService.update_program(instance, **validated_data)
>>>>>>> 增加filter 和 log


class ReadOnlyProgramSerializer(serializers.ModelSerializer):
    '''Indicate how to serialize read_only Program instance.'''
    category_str = serializers.CharField(source='get_category_display',
                                         read_only=True)
    department = serializers.SlugField(read_only=True,
                                       source='department.name')

    class Meta:
        model = Program
        fields = '__all__'
