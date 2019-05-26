'''user core statistics service'''
from collections import defaultdict

from django.core.cache import cache
from django.db import models
from django.db.models import functions
from django.utils.timezone import now

from training_event.models import Enrollment, EventCoefficient
from training_record.models import Record


class UserCoreStatisticsService:
    '''Provide access to user' core statistics data.'''
    @staticmethod
    def get_competition_award_info(user, context=None):
        '''Latest competition award info.

        Parameters
        ----------
        user: User
        context: dict
            This context dictionary should have necessary keys specified in
            SummaryParametersSerializer.

        Return
        ------
        data: dict
            {
                timestamp: datetime
                    The time when this data was generated.
                data: dict
                    Award info. None if no records found.
                    {
                        competition: str
                            The name of the competition.
                        level: str
                            The competition level, e.g.: 校级，省级，国家级
                        award: str
                            The award ranking, e.g.: 一等奖，优秀奖
                    }
            }
        '''
        end_time = context['end_time']
        start_time = context['start_time']
        end_time_key = end_time.strftime("%Y-%m-%dT%H:%M:%S%z")
        start_time_key = start_time.strftime("%Y-%m-%dT%H:%M:%S%z")
        cache_key = (
            f'competition_award_info:{user.id}'
            f'_{start_time_key}_{end_time_key}'
        )

        cached_value = cache.get(cache_key)
        if cached_value:
            return cached_value
        competition_award_info = (
            Record.objects
            .filter(user=user)
            .filter(campus_event__name__regex=r'(校|市|省|国家)级(.*奖)')
            .filter(create_time__gte=start_time)
            .filter(create_time__lte=end_time)
            .order_by('-campus_event__time')
            .values_list('campus_event__name', flat=True)
            .first()
        )
        if competition_award_info:
            competition_award_info = competition_award_info.split('|')
            res = dict(zip(
                ('competition', 'level', 'award'),
                competition_award_info
            ))
        else:
            res = None
        res = {
            'timestamp': now(),
            'start_time': start_time_key,
            'end_time': end_time_key,
            'data': res,
        }
        cache.set(cache_key, res, 8 * 3600)  # Cache for 8 hours
        return res

    @staticmethod
    def get_monthly_added_records_statistics(
            user, context=None):  # pylint: disable=unused-argument
        '''Latest added records (last 12 months).

        Parameters
        ----------
        user: User
        context: dict
            This context dictionary should have necessary keys specified in
            SummaryParametersSerializer.

        Return
        ------
        data: dict
            {
                timestamp: datetime
                    The time when this data was generated.
                months: list of str
                    The month labels.
                campus_data: list of int
                    The number of added campus records w.r.t months.
                off_campus_data: list of int
                    The number of added off-campus records w.r.t months.
            }
        '''
        cache_key = f'monthly_added_records_statistics:{user.id}'
        cached_value = cache.get(cache_key)
        if cached_value:
            return cached_value
        monthly_records = (
            Record.objects
            .filter(user=user)
            .annotate(
                month=functions.TruncMonth('create_time'),
            )
            .values('month')
            .annotate(
                campus_count=models.Count('campus_event'),
                off_campus_count=models.Count('off_campus_event'))
            .order_by('-month')
            .values('month', 'campus_count', 'off_campus_count')[:12]
        )
        monthly_records = list(monthly_records)[::-1]
        res = {
            'timestamp': now(),
            'months': [x['month'].strftime('%Y年%m月') for x in monthly_records],
            'campus_data': [x['campus_count'] for x in monthly_records],
            'off_campus_data': [
                x['off_campus_count'] for x in monthly_records],
        }
        cache.set(cache_key, res, 8 * 3600)  # Cache for 8 hours
        return res

    @staticmethod
    def get_records_statistics(user, context=None):
        '''User's records statistics.

        Parameters
        ----------
        user: User
        context: dict
            This context dictionary should have necessary keys specified in
            SummaryParametersSerializer.

        Return
        ------
        data: dict
            {
                timestamp: datetime
                    The time when this data was generated.
                num_campus_records: int
                    The number of campus event records.
                num_off_campus_records: int
                    The number of off-campus event records.
                campus_records_percent: str
                    The ratio of campus event records in all records.
                off_campus_records_percent: str
                    The ratio of off-campus event records in all records.
            }
        '''
        end_time = context['end_time']
        start_time = context['start_time']
        end_time_key = end_time.strftime("%Y-%m-%dT%H:%M:%S%z")
        start_time_key = start_time.strftime("%Y-%m-%dT%H:%M:%S%z")
        cache_key = (
            f'records_statistics:{user.id}'
            f'_{start_time_key}_{end_time_key}'
        )
        cached_value = cache.get(cache_key)
        if cached_value:
            return cached_value
        num_campus_records = (
            Record.objects
            .filter(user=user, campus_event__isnull=False)
            .filter(create_time__gte=start_time)
            .filter(create_time__lte=end_time)
            .count()
        )
        num_off_campus_records = (
            Record.objects
            .filter(user=user, off_campus_event__isnull=False)
            .filter(create_time__gte=start_time)
            .filter(create_time__lte=end_time)
            .count()
        )
        total_records = num_campus_records + num_off_campus_records
        campus_records_ratio = (
            num_campus_records / total_records if total_records else 0
        )
        off_campus_records_ratio = (
            1 - campus_records_ratio if total_records else 0
        )
        campus_records_ratio = f'{campus_records_ratio:.0%}'
        off_campus_records_ratio = f'{off_campus_records_ratio:.0%}'
        res = {
            'timestamp': now(),
            'start_time': start_time_key,
            'end_time': end_time_key,
            'num_campus_records': num_campus_records,
            'num_off_campus_records': num_off_campus_records,
            'campus_records_ratio': campus_records_ratio,
            'off_campus_records_ratio': off_campus_records_ratio,
        }
        cache.set(cache_key, res, 3600)  # Cache for 8 hours
        return res

    # pylint: disable=too-many-locals
    @staticmethod
    def get_events_statistics(user, context=None):
        '''User's events statistics.

        Parameters
        ----------
        user: User
        context: dict
            This context dictionary should have necessary keys specified in
            SummaryParametersSerializer.

        Return
        ------
        data: dict
            {
                timestamp: datetime
                    The time when this data was generated.
                num_enrolled_events: int
                    The number of registered events.
                num_completed_events: int
                    The number of completed events.
                num_events_as_exprt: int
                    The number of events participated as expert.
            }
        '''
        end_time = context['end_time']
        start_time = context['start_time']
        end_time_key = end_time.strftime("%Y-%m-%dT%H:%M:%S%z")
        start_time_key = start_time.strftime("%Y-%m-%dT%H:%M:%S%z")
        cache_key = (
            f'events_statistics:{user.id}'
            f'_{start_time_key}_{end_time_key}'
        )
        cached_value = cache.get(cache_key)
        if cached_value:
            return cached_value
        records = (
            Record.objects
            .filter(user=user, campus_event__isnull=False)
            .filter(create_time__gte=start_time)
            .filter(create_time__lte=end_time)
            .select_related('campus_event__program')
        )
        num_completed_events = len(records)
        # num_enrolled_events =   enrolled events
        #                       + not enrolled events (but completed)

        # Enrolled
        enrolled_events = (
            Enrollment.objects
            .filter(user=user)
            .filter(create_time__gte=start_time)
            .filter(create_time__lte=end_time)
            .values_list('campus_event', flat=True)
        )
        num_enrolled_events = len(enrolled_events)
        # Not enrolled, but completed
        num_not_enrolled_events = (
            Record.objects
            .filter(user=user)
            .exclude(campus_event_id__in=enrolled_events)
            .filter(create_time__gte=start_time)
            .filter(create_time__lte=end_time)
            .count()
        )
        num_enrolled_events += num_not_enrolled_events

        num_events_as_expert = (
            Record.objects
            .filter(user=user)
            .filter(event_coefficient__role=EventCoefficient.ROLE_EXPERT)
            .filter(create_time__gte=start_time)
            .filter(create_time__lte=end_time)
            .count()
        )
        res = {
            'timestamp': now(),
            'start_time': start_time_key,
            'end_time': end_time_key,
            'num_enrolled_events': num_enrolled_events,
            'num_completed_events': num_completed_events,
            'num_events_as_expert': num_events_as_expert,
        }
        cache.set(cache_key, res, 8 * 3600)  # Cache for 8 hours
        return res

    @staticmethod
    def get_programs_statistics(user, context=None):
        '''User's programs statistics.

        Parameters
        ----------
        user: User
        context: dict
            This context dictionary should have necessary keys specified in
            SummaryParametersSerializer.

        Return
        ------
        data: dict
            {
                timestamp: datetime
                    The time when this data was generated.
                programs: list of str
                    The programs that user participated in.
                data: list of dict
                    The statistics to the participated programs.
            }
        '''
        end_time = context['end_time']
        start_time = context['start_time']
        end_time_key = end_time.strftime("%Y-%m-%dT%H:%M:%S%z")
        start_time_key = start_time.strftime("%Y-%m-%dT%H:%M:%S%z")
        cache_key = (
            f'programs_statistics:{user.id}'
            f'_{start_time_key}_{end_time_key}'
        )
        cached_value = cache.get(cache_key)
        if cached_value:
            return cached_value
        program_names = (
            Record.objects
            .filter(user=user, campus_event__isnull=False)
            .select_related('campus_event__program')
            .filter(create_time__gte=start_time)
            .filter(create_time__lte=end_time)
            .values_list('campus_event__program__name', flat=True)
        )

        # Participated programs
        programs = defaultdict(int)
        for name in program_names:
            programs[name] += 1
        res = {
            'timestamp': now(),
            'start_time': start_time_key,
            'end_time': end_time_key,
            'data': [{'name': key, 'value': value}
                     for key, value in programs.items()],
            'programs': list(programs.keys()),
        }
        cache.set(cache_key, res, 8 * 3600)  # Cache for 8 hours
        return res
