'''Provide services of data graph.'''
import math
from collections import defaultdict

from django.core.cache import cache
from django.db import models
from django.db.models import functions
from django.db.models.functions import Coalesce
from django.contrib.auth import get_user_model
from django.utils.timezone import now

from auth.models import Department
from infra.exceptions import BadRequest
from training_event.models import Enrollment, EventCoefficient
from training_record.models import Record
from data_warehouse.models import Ranking


class UserRankingService:
    '''Provide access to ranking-related data.'''
    @classmethod
    def _get_ranking(cls, user, department_id, ranking_type):
        ranking = (
            Ranking.objects
            .filter(user=user)
            .filter(ranking_type=ranking_type)
            .filter(department_id=department_id)
        )
        if not ranking:
            return '暂无数据'
        ranking = ranking[0].ranking
        total = (
            Ranking.objects
            .filter(ranking_type=ranking_type)
            .filter(department_id=department_id)
            .count() + 1e-5
        )
        ranking = cls.round_ranking_float(ranking / total)
        ranking = f'前 {ranking:.0%}'
        return ranking

    @classmethod
    def get_total_training_hours_ranking_in_department(cls, user):
        '''
        Human-readable string for user's ranking in department (by total
        training hours).

        Parameters
        ----------
        user: User

        Return
        ------
        data: dict
            {
                timestamp: datetime
                    The time when this data was generated.
                ranking: str
                    The string indicating user's ranking. e.g.: 前5%
            }
        '''
        cache_key = f'total_training_hours_ranking_in_department:{user.id}'
        cached_value = cache.get(cache_key)
        if cached_value:
            return cached_value
        ranking = cls._get_ranking(
            user,
            user.administrative_department_id,
            Ranking.RANKING_BY_TOTAL_TRAINING_HOURS
        )
        res = {
            'timestamp': now(),
            'ranking': ranking,
        }
        cache.set(cache_key, res, 8 * 3600)  # Cache for 8 hours
        return res

    @classmethod
    def get_total_training_hours_ranking_in_school(cls, user):
        '''
        Human-readable string for user's ranking in school (by total
        training hours).

        Parameters
        ----------
        user: User

        Return
        ------
        data: dict
            {
                timestamp: datetime
                    The time when this data was generated.
                ranking: str
                    The string indicating user's ranking. e.g.: 前5%
            }
        '''
        cache_key = f'total_training_hours_ranking_in_school:{user.id}'
        cached_value = cache.get(cache_key)
        if cached_value:
            return cached_value
        dlut_department_id = Department.objects.get(name='大连理工大学').id
        ranking = cls._get_ranking(
            user,
            dlut_department_id,
            Ranking.RANKING_BY_TOTAL_TRAINING_HOURS
        )
        res = {
            'timestamp': now(),
            'ranking': ranking,
        }
        cache.set(cache_key, res, 8 * 3600)  # Cache for 8 hours
        return res

    @staticmethod
    def round_ranking_float(ranking_float):
        '''
        Round percent to nearest multiple of 0.05 (ceil mode) and
        cut into [0, 1].
        '''
        ranking_float = math.ceil(ranking_float * 20) / 20
        ranking_float = max(0, min(1, ranking_float))
        return ranking_float

    @staticmethod
    def generate_user_rankings_by_training_hours(baseoffset=0):
        '''Calculate user rankings by training hours.'''
        dlut_department = Department.objects.get(name='大连理工大学').id
        User = get_user_model()
        user_training_hours = list(
            User.objects
            .filter(administrative_department__isnull=False)
            .prefetch_related(
                models.Prefetch('record_set', Record.objects.filter(
                    status__in=(
                        Record.STATUS_SCHOOL_ADMIN_APPROVED,
                        Record.STATUS_FEEDBACK_REQUIRED,
                        Record.STATUS_SUBMITTED,
                    )
                )),
                'record_set__campus_event',
                'record_set__off_campus_event'
            )
            .annotate(
                campus_hours=Coalesce(
                    models.Sum('record__campus_event__num_hours'), 0),
                off_campus_hours=Coalesce(
                    models.Sum('record__off_campus_event__num_hours'), 0),
            )
            .annotate(
                total_hours=(
                    models.F('campus_hours')+models.F('off_campus_hours')
                )
            )
            .order_by('-campus_hours')
            .values(
                'id', 'administrative_department', 'campus_hours',
                'off_campus_hours', 'total_hours'
            )
        )
        # Ranking by training hours
        rankings = []
        ranking_tasks = (
            (
                Ranking.RANKING_BY_TOTAL_TRAINING_HOURS,
                lambda x: x['total_hours'],
            ),
            (
                Ranking.RANKING_BY_CAMPUS_TRAINING_HOURS,
                lambda x: x['campus_hours'],
            ),
            (
                Ranking.RANKING_BY_OFF_CAMPUS_TRAINING_HOURS,
                lambda x: x['off_campus_hours'],
            ),
        )
        offset = baseoffset
        department_rankings = defaultdict(lambda: 1)

        def get_ranking_in_department(department):
            val = department_rankings[department]
            department_rankings[department] += 1
            return val
        for ranking_type, value_func in ranking_tasks:
            user_training_hours.sort(key=value_func, reverse=True)
            # Rank in administrative_department
            rankings.extend(Ranking(
                id=idx + offset,
                ranking_type=ranking_type,
                department_id=x['administrative_department'],
                ranking=get_ranking_in_department(
                    x['administrative_department']),
                user_id=x['id'],
                value=value_func(x)
            ) for idx, x in enumerate(user_training_hours, 1))
            offset += len(user_training_hours)
            # Rank among all departments
            rankings.extend(Ranking(
                id=idx + offset,
                ranking_type=ranking_type,
                department_id=dlut_department,
                ranking=get_ranking_in_department(dlut_department),
                user_id=x['id'],
                value=value_func(x)
            ) for idx, x in enumerate(user_training_hours, 1))
            offset += len(user_training_hours)

        Ranking.objects.bulk_create(rankings)
        return offset

    @classmethod
    def generate_user_rankings(cls):
        '''Generate all kinds of user rankings.
        This function normally should be registered and invoked automatically
        by Celery.
        '''
        Ranking.objects.all().delete()
        baseoffset = 0
        baseoffset = cls.generate_user_rankings_by_training_hours(baseoffset)


class UserCoreStatisticsService:
    '''Provide access to user' core statistics data.'''
    @staticmethod
    def get_competition_award_info(user):
        '''Latest competition award info.

        Parameters
        ----------
        user: User

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
        cache_key = f'competition_award_info:{user.id}'
        cached_value = cache.get(cache_key)
        if cached_value:
            return cached_value
        competition_award_info = (
            Record.objects
            .filter(user=user)
            .filter(campus_event__name__regex=r'(校|市|省|国家)级(.*奖)')
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
            'data': res,
        }
        cache.set(cache_key, res, 8 * 3600)  # Cache for 8 hours
        return res

    @staticmethod
    def get_monthly_added_records_statistics(user):
        '''Latest added records (last 12 months).

        Parameters
        ----------
        user: User

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
    def get_records_statistics(user):
        '''User's records statistics.

        Parameters
        ----------
        user: User

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
        cache_key = f'records_statistics:{user.id}'
        cached_value = cache.get(cache_key)
        if cached_value:
            return cached_value
        num_campus_records = (
            Record.objects
            .filter(user=user, campus_event__isnull=False)
            .count()
        )
        num_off_campus_records = (
            Record.objects
            .filter(user=user, off_campus_event__isnull=False)
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
            'num_campus_records': num_campus_records,
            'num_off_campus_records': num_off_campus_records,
            'campus_records_ratio': campus_records_ratio,
            'off_campus_records_ratio': off_campus_records_ratio,
        }
        cache.set(cache_key, res, 8 * 3600)  # Cache for 8 hours
        return res

    @staticmethod
    def get_events_statistics(user):
        '''User's events statistics.

        Parameters
        ----------
        user: User

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
        cache_key = f'events_statistics:{user.id}'
        cached_value = cache.get(cache_key)
        if cached_value:
            return cached_value
        records = (
            Record.objects
            .filter(user=user, campus_event__isnull=False)
            .select_related('campus_event__program')
        )
        num_completed_events = len(records)
        # num_enrolled_events =   enrolled events
        #                       + not enrolled events (but completed)

        # Enrolled
        enrolled_events = Enrollment.objects.filter(user=user).values_list(
            'campus_event', flat=True)
        num_enrolled_events = len(enrolled_events)
        # Not enrolled, but completed
        num_not_enrolled_events = (
            Record.objects
            .filter(user=user)
            .exclude(campus_event_id__in=enrolled_events)
            .count()
        )
        num_enrolled_events += num_not_enrolled_events

        num_events_as_expert = (
            Record.objects
            .filter(user=user)
            .filter(event_coefficient__role=EventCoefficient.ROLE_EXPERT)
            .count()
        )
        res = {
            'timestamp': now(),
            'num_enrolled_events': num_enrolled_events,
            'num_completed_events': num_completed_events,
            'num_events_as_expert': num_events_as_expert,
        }
        cache.set(cache_key, res, 8 * 3600)  # Cache for 8 hours
        return res

    @staticmethod
    def get_programs_statistics(user):
        '''User's programs statistics.

        Parameters
        ----------
        user: User

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
        cache_key = f'programs_statistics:{user.id}'
        cached_value = cache.get(cache_key)
        if cached_value:
            return cached_value
        program_names = (
            Record.objects
            .filter(user=user, campus_event__isnull=False)
            .select_related('campus_event__program')
            .values_list('campus_event__program__name', flat=True)
        )

        # Participated programs
        programs = defaultdict(int)
        for name in program_names:
            programs[name] += 1
        res = {
            'timestamp': now(),
            'data': [{'name': key, 'value': value}
                     for key, value in programs.items()],
            'programs': list(programs.keys()),
        }
        cache.set(cache_key, res, 8 * 3600)  # Cache for 8 hours
        return res


class AggregateDataService:
    '''provide services for getting data'''

    STAFF_STATISTICS = 0
    TRAINEE_STATISTICS = 1
    FULL_TIME_TEACHER_TRAINED_COVERAGE = 2
    TRAINING_HOURS_WORKLOAD_STATISTICS = 3

    BY_DEPARTMENT = 0
    BY_TEACHING_TYPE = 1
    BY_STAFF_TITLE = 2
    BY_HIGHEST_DEGREE = 3
    BY_AGE_DISTRIBUTION = 4

    BY_DEPARTMENT = 0
    BY_STAFF_TITLE = 1
    BY_AGE_DISTRIBUTION = 2

    BY_TOTAL_STAFF_NUM = 0
    BY_TOTAL_TRAINING_HOURS = 1
    BY_PER_CAPITA_TRAINING_HOURS = 2
    BY_TOTAL_WORKLOAD = 3
    BY_PER_CAPITA_WORKLOAD = 4

    STAFF_GROUPING_CHOICES = (
        (BY_DEPARTMENT, '按学院', 'BY_DEPARTMENT'),
        (BY_TEACHING_TYPE, '按人员类别', 'BY_TEACHING_TYPE'),
        (BY_STAFF_TITLE, '按职称', 'BY_STAFF_TITLE'),
        (BY_HIGHEST_DEGREE, '按最高学位', 'BY_HIGHEST_DEGREE'),
        (BY_AGE_DISTRIBUTION, '按年龄分布', 'BY_AGE_DISTRIBUTION')
    )
    TRAINEE_GROUPING_CHOICES = (
        (BY_DEPARTMENT, '按学院', 'BY_DEPARTMENT'),
        (BY_STAFF_TITLE, '按职称', 'BY_STAFF_TITLE'),
        (BY_AGE_DISTRIBUTION, '按年龄分布', 'BY_AGE_DISTRIBUTION')
    )
    TRAINING_HOURS_GROUPING_CHOICES = (
        (BY_TOTAL_STAFF_NUM, '按总人数', 'BY_TOTAL_STAFF_NUM'),
        (BY_TOTAL_TRAINING_HOURS, '按总培训学时', 'BY_TOTAL_TRAINING_HOURS'),
        (BY_PER_CAPITA_TRAINING_HOURS, '按人均培训学时', 'BY_PER_CAPITA_\
            TRAINING_HOURS'),
        (BY_TOTAL_WORKLOAD, '按总工作量', 'BY_TOTAL_WORKLOAD'),
        (BY_PER_CAPITA_WORKLOAD, '按人均工作量', 'BY_PER_CAPITA_WORKLOAD')
    )

    @classmethod
    def dispatch(cls, method_name, context):
        '''to call a specific service for getting data'''
        available_method_list = (
            'staff_statistics',
            'trainee_statistics',
            'coverage_statistics',
            'training_hours_statistics',
            'personal_summary',
        )
        handler = getattr(cls, method_name, None)
        if method_name not in available_method_list or handler is None:
            raise BadRequest("错误的参数")
        return handler(context)

    @staticmethod
    def personal_summary(context):
        '''Populate an overview of training statistics for the user.'''
        request = context.get('request', None)
        if request is None:
            raise BadRequest('参数错误')
        user = request.user

        res = {
            'programs_statistics': (
                UserCoreStatisticsService.get_programs_statistics(user)
            ),
            'events_statistics': (
                UserCoreStatisticsService.get_events_statistics(user)
            ),
            'records_statistics': (
                UserCoreStatisticsService.get_records_statistics(user)
            ),
            'competition_award_info': (
                UserCoreStatisticsService.get_competition_award_info(user)
            ),
            'monthly_added_records': (
                UserCoreStatisticsService
                .get_monthly_added_records_statistics(user)
            ),
            'ranking_in_department': (
                UserRankingService
                .get_total_training_hours_ranking_in_department(user)
            ),
            'ranking_in_school': (
                UserRankingService
                .get_total_training_hours_ranking_in_school(user)
            ),
        }
        return res

    @classmethod
    def staff_statistics(cls, context):
        '''to get staff statistics data'''

    @classmethod
    def trainee_statistics(cls, context):
        '''to get trainee statistics data'''

    @classmethod
    def coverage_statistics(cls, context):
        '''to get coverage statistics data'''

    @classmethod
    def training_hours_statistics(cls, context):
        '''to get training hours statistics data'''

    @staticmethod
    def group_by_teaching_type(objects, start_year, end_year, region):
        '''group data by teaching type'''

    @staticmethod
    def tuple_to_dict_list(data):
        '''return a data dict list'''
        return [{
            'type': type_num,
            'name': name,
            'key': key_name
            } for type_num, name, key_name in data]

    @classmethod
    def get_canvas_options(cls):
        '''return a data graph select dictionary'''
        statistics_type = [
            {'type': cls.STAFF_STATISTICS,
             'name': '教职工人数统计',
             'key': 'STAFF_STATISTICS',
             'subOption': cls.tuple_to_dict_list(cls.STAFF_GROUPING_CHOICES)},
            {'type': cls.TRAINEE_STATISTICS,
             'name': '培训人数统计',
             'key': 'TRAINEE_STATISTICS',
             'subOption': cls.tuple_to_dict_list(
                 cls.TRAINEE_GROUPING_CHOICES)},
            {'type': cls.FULL_TIME_TEACHER_TRAINED_COVERAGE,
             'name': '专任教师培训覆盖率统计',
             'key': 'FULL_TIME_TEACHER_TRAINED_COVERAGE',
             'subOption': cls.tuple_to_dict_list(
                 cls.TRAINEE_GROUPING_CHOICES)},
            {'type': cls.TRAINING_HOURS_WORKLOAD_STATISTICS,
             'name': '培训学时与工作量统计',
             'key': 'TRAINING_HOURS_WORKLOAD_STATISTICS',
             'subOption': cls.tuple_to_dict_list(
                 cls.TRAINING_HOURS_GROUPING_CHOICES)}
        ]
        return statistics_type
