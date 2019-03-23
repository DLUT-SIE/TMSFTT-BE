''' Provide filters used in filtering logic. '''
from django_filters import rest_framework as filters

from training_event.models import OffCampusEvent


class OffCampusEventFilter(filters.FilterSet):
    '''Provide required information about filtering OffCampusEvent.'''
    class Meta:
        model = OffCampusEvent
        fields = {
            'name': ['startswith'],
        }
