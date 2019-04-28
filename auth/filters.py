''' Provide filters used in filtering logic. '''
from django_filters import rest_framework as filters

from auth.models import Group


class GroupFilter(filters.FilterSet):
    '''Provide required information about filtering Group'''
    class Meta:
        model = Group
        fields = {
            'name': ['startswith'],
        }
