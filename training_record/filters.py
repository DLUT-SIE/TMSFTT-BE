''' Provide filters used in filtering logic. '''
import django_filters
from django_filters import rest_framework as filters
from django.db.models import Q

from training_record.models import Record, RecordContent, RecordAttachment


# pylint: disable=unused-argument
class RecordFilter(filters.FilterSet):
    '''Provide required information about filtering Record.'''
    event_name = django_filters.CharFilter(label='活动名称',
                                           method='filter_event_name')
    event_location = django_filters.CharFilter(label='活动地点',
                                               method='filter_event_location')
    start_time = django_filters.DateTimeFilter(label='起始时间',
                                               method='filter_start_time')
    end_time = django_filters.DateTimeFilter(label='截止时间',
                                             method='filter_end_time')

    def filter_event_name(self, queryset, name, value):
        '''Filter event name'''
        return queryset.filter(
            Q(off_campus_event__name__startswith=value) |
            Q(campus_event__name__startswith=value))

    def filter_event_location(self, queryset, name, value):
        '''Filter event location'''
        return queryset.filter(
            Q(off_campus_event__location__startswith=value) |
            Q(campus_event__location__startswith=value))

    def filter_start_time(self, queryset, name, value):
        '''Filter event name'''
        return queryset.filter(
            Q(off_campus_event__time__gte=value) |
            Q(campus_event__time__gte=value))

    def filter_end_time(self, queryset, name, value):
        '''Filter event name'''
        return queryset.filter(
            Q(off_campus_event__time__lte=value) |
            Q(campus_event__time__lte=value))

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
