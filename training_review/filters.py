''' Provide filters used in filtering logic. '''
from django_filters import rest_framework as filters

from training_review.models import ReviewNote


class ReviewNoteFilter(filters.FilterSet):
    '''Provide required information about filtering ReviewNote.'''
    class Meta:
        model = ReviewNote
        fields = {
            'record': ['exact'],
            'user': ['exact'],
        }
