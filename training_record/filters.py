''' Provide filters used in filtering logic. '''
from django_filters import rest_framework as filters

from training_record.models import Record


class RecordFilter(filters.FilterSet):
    '''Provide required information about filtering Record.'''
    class Meta:
        model = Record
        fields = {
            'off_campus_event': ['isnull'],
        }
