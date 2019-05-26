''' Provide filters used in filtering logic. '''
from django_filters import rest_framework as filters

from training_program.models import Program


class ProgramFilter(filters.FilterSet):
    '''Provide required information about filtering Program.'''
    class Meta:
        model = Program
        fields = {
            'department': ['exact'],
            'department__name': ['exact'],
        }
