'''school core statistics service'''
from django.core.cache import cache
from django.db import models
from django.db.models import Q, Count, functions
from django.utils.timezone import now

from training_event.models import CampusEvent
from training_record.models import Record
from auth.services import UserService


class SchoolCoreStatisticsService:
    '''Provide access to school' core statistics data.'''
    @staticmethod
    def get_events_statistics():
        '''Populate events statistics for whole school.

        Return
        ------
        data: dict
            {
                timestamp: datetime
                    The time when this data was generated.
                available_to_enroll: int
                    The number of events which are available to enroll. 
            }
        '''
        cache_key = 'events_statistics'
        cached_value = cache.get(cache_key)
        if cached_value:
            return cached_value
        current_time = now()
        res = {
            'timestamp': current_time,
            'available_to_enroll': (
                CampusEvent.objects.filter(deadline__gt=current_time).count()
            ),
        }
        cache.set(cache_key, res, 8 * 3600)
        return res

    @staticmethod
    def get_records_statistics():
        '''Populate records statistics for whole school.

        Return
        ------
        data: dict
            {
                timestamp: datetime
                    The time when this data was generated.
                num_records: int
                    The total number of records
                num_records_added_in_current_month: int
                    The number of records added in this month
                num_average_records: float
                    The average number of records per user
            }
        '''
        cache_key = 'records_statistics'
        cached_value = cache.get(cache_key)
        if cached_value:
            return cached_value
        current_time = now()

        # The total number of records
        num_records = (
            Record.objects
            .filter(
                Q(campus_event__isnull=False)
                | Q(status=Record.STATUS_SCHOOL_ADMIN_APPROVED)
            ).count()
        )

        # The number of records added in this month
        num_records_added_in_current_month = (
            Record.objects
            .filter(create_time__gte=current_time.replace(
                day=1, hour=0, minute=0, second=0))
            .count()
        )

        num_users = UserService.get_full_time_teachers().count()
        num_average_records = num_records / num_users if num_users else 0
        res = {
            'timestamp': current_time,
            'num_records': num_records,
            'num_records_added_in_current_month': (
                num_records_added_in_current_month
            ),
            'num_average_records': num_average_records
        }
        cache.set(cache_key, res, 8 * 3600)
        return res

    @staticmethod
    def get_department_records_statistics():
        '''Populate records statistics for departments in current year.

        Return
        ------
        data: dict
            {
                timestamp: datetime
                    The time when this data was generated.
                data : dict
                    {
                        department: str
                            The name of the department
                        num_users: int
                            The number of users in this department
                        num_records: int
                            The number of records created in this department
                            in this year
                    }
        '''
        cache_key = 'department_records_statistics'
        cached_value = cache.get(cache_key)
        if cached_value:
            return cached_value
        current_time = now()
        grouped_counts = (
            Record.objects
            .filter(
                Q(campus_event__isnull=False)
                | Q(status=Record.STATUS_SCHOOL_ADMIN_APPROVED)
            )
            .filter(create_time__gte=current_time.replace(
                month=1, day=1, hour=0, minute=0, second=0))
            .annotate(
                department_name=models.F(
                    'user__administrative_department__name'
                )
            )
            .values('department_name')
            .annotate(count=Count('id'))
            .order_by('-count')
        )
        grouped_users = {x['department_name']: x['count'] for x in (
            UserService.get_full_time_teachers()
            .annotate(
                department_name=models.F('administrative_department__name'))
            .values('department_name')
            .annotate(count=Count('id'))
        )}
        data = []
        for item in grouped_counts:
            department_name = item['department_name']
            num_records = item['count']
            num_users = grouped_users.get(department_name, 0)
            data.append({
                'department': department_name,
                'num_users': num_users,
                'num_records': num_records,
            })
        res = {
            'timestamp': current_time,
            'data': data
        }
        cache.set(cache_key, res, 8 * 3600)
        return res

    @staticmethod
    def get_monthly_added_records_statistics():
        '''Populate records statistics for recent 12 months.'''
        cache_key = 'monthly_added_records_statistics'
        cached_value = cache.get(cache_key)
        if cached_value:
            return cached_value
        current_time = now()
        monthly_records = (
            Record.objects
            .filter(
                Q(campus_event__isnull=False)
                | Q(status=Record.STATUS_SCHOOL_ADMIN_APPROVED)
            )
            .filter(create_time__gte=current_time.replace(
                year=current_time.year-1, day=1,
                hour=0, minute=0, second=0))
            .annotate(
                month=functions.TruncMonth('create_time'),
            )
            .values('month')
            .annotate(count=Count('id'))
            .order_by('month')
        )
        res = {
            'timestamp': current_time,
            'months': [
                x['month'].strftime('%Y年%m月') for x in monthly_records],
            'records': [x['count'] for x in monthly_records]
        }
        cache.set(cache_key, res, 8 * 3600)
        return res
