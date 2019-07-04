''' Provide filters used in filtering logic. '''
from django_filters import rest_framework as filters

from training_event.models import OffCampusEvent
from training_event.models import CampusEvent


class OffCampusEventFilter(filters.FilterSet):
    '''Provide required information about filtering OffCampusEvent.'''
    class Meta:
        model = OffCampusEvent
        fields = {
            'name': ['startswith'],
            'id': ['in'],
        }


class CampusEventFilter(filters.FilterSet):
    '''Provide required information about filtering CampusEvent.'''
    class Meta:
        model = CampusEvent
        fields = {
            'program': ['exact'],
            'id': ['in'],
            'reviewed': ['exact'],
            'name': ['icontains'],
            
        }
