'''Define how to serialize our models.'''
from rest_framework import serializers

import training_program.models


class ProgramCatgegorySerializer(serializers.ModelSerializer):
    '''Indicate how to serialize ProgramCatgegory instance.'''
    class Meta:
        model = training_program.models.ProgramCatgegory
        fields = '__all__'


class ProgramFormSerializer(serializers.ModelSerializer):
    '''Indicate how to serialize ProgramForm instance.'''
    class Meta:
        model = training_program.models.ProgramForm
        fields = '__all__'


class ProgramSerializer(serializers.ModelSerializer):
    '''Indicate how to serialize Program instance.'''
    class Meta:
        model = training_program.models.Program
        fields = '__all__'
