'''Define how to serialize our models.'''
from rest_framework import serializers

from training_program.models import Program


class ProgramSerializer(serializers.ModelSerializer):
    '''Indicate how to serialize Program instance.'''
    category_str = serializers.CharField(source='get_category_display',
                                         read_only=True)
    department = serializers.SlugField(read_only=True, source='name')

    class Meta:
        model = Program
        fields = '__all__'
