''' Provide filters used in filtering logic. '''
from django_filters import rest_framework as filters

from training_record.models import Record, RecordContent, RecordAttachment


class RecordFilter(filters.FilterSet):
    '''Provide required information about filtering Record.'''
    class Meta:
        model = Record
        fields = {
            'off_campus_event': ['isnull'],
        }


class RecordContentFilter(filters.FilterSet):
    '''Provide required information about filtering RecordContent.'''
    class Meta:
        model = RecordContent
        fields = {
            'id': ['in'],
        }


class RecordAttachmentFilter(filters.FilterSet):
    '''Provide required information about filtering RecordAttachment.'''
    class Meta:
        model = RecordAttachment
        fields = {
            'id': ['in'],
        }
