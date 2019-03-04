'''Define how to serialize our models.'''
from rest_framework import serializers

from training_program.models import (
    Program, ProgramCategory, ProgramForm
)
from auth.serializers import DepartmentSerializer


class ProgramCategorySerializer(serializers.ModelSerializer):
    '''Indicate how to serialize ProgramCategory instance.'''
    class Meta:
        model = ProgramCategory
        fields = '__all__'


class ProgramFormSerializer(serializers.ModelSerializer):
    '''Indicate how to serialize ProgramForm instance.'''
    class Meta:
        model = ProgramForm
        fields = '__all__'


class ProgramSerializer(serializers.ModelSerializer):
    '''Indicate how to serialize Program instance.'''
    department_detail = DepartmentSerializer(source='department',
                                             read_only=True)
    category_detail = ProgramCategorySerializer(source='category',
                                                read_only=True)

    class Meta:
        model = Program
        fields = '__all__'
