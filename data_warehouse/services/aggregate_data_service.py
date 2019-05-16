'''Provide services of data aggregate.'''
from django.contrib.auth import get_user_model
from django.db.models import Count
from django.utils.timezone import datetime, make_aware

from auth.models import Department
from auth.services import DepartmentService
from data_warehouse.services.user_core_statistics_service import (
    UserCoreStatisticsService
)
from data_warehouse.services.user_ranking_service import (
    UserRankingService
)
from data_warehouse.consts import EnumData
from infra.exceptions import BadRequest
from training_record.models import Record


class AggregateDataService:
    '''provide services for getting data'''

    @classmethod
    def dispatch(cls, method_name, context):
        '''to call a specific service for getting data'''
        available_method_list = (
            'teachers_statistics',
            'records_statistics',
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
    def teachers_statistics(cls, context):
        ''' get teachers statistics data'''
        group_by = context.get('group_by', '')
        department_id = context.get('department_id', '')
        if group_by.isdigit() and department_id.isdigit():
            group_by = int(group_by)
            department_id = int(department_id)
        else:
            raise BadRequest("错误的参数")
        users = cls.get_users_by_department(
            context['request'].user, department_id)
        group_users = TeachersGroupService.teachers_statistics_group_dispatch(
            users, group_by, True)
        data = CanvasDataFormat.teachers_statistics_data_format(group_users)
        return data

    @staticmethod
    def get_users_by_department(request_user, department_id):
        '''get users objects by department.
        Parameters
        ----------
        request_user: User
        department_id: int
        '''
        departments = Department.objects.filter(id=department_id)
        if departments:
            department = departments[0]
            if request_user.is_school_admin:
                if department.name == '大连理工大学':
                    return get_user_model().objects.all()
                return get_user_model().objects.filter(
                    administrative_department=department)
            if request_user.check_department_admin(department):
                return get_user_model().objects.filter(
                    administrative_department=department)
        return get_user_model().objects.none()

    @classmethod
    def records_statistics(cls, context):
        ''' get records statistics data'''
        group_by = context.get('group_by', '')
        start_year = context.get('start_year', 2016)
        end_year = context.get('end_year', 2016)
        department_id = context.get('department_id', '')
        if group_by.isdigit() and start_year.isdigit() and\
                end_year.isdigit() and department_id.isdigit():
            group_by = int(group_by)
            start_year = int(start_year)
            end_year = int(end_year)
            department_id = int(department_id)
        else:
            raise BadRequest("错误的参数")
        time = {'start': start_year, 'end': end_year}
        records = cls.get_records_by_time_department(
            context['request'].user, department_id, time)
        group_records = {}
        group_records['campus_records'] = (
            RecordsGroupService.records_statistics_group_dispatch(
                records['campus_records'], group_by, True)
        )
        group_records['off_campus_records'] = (
            RecordsGroupService.records_statistics_group_dispatch(
                records['off_campus_records'], group_by, True)
        )
        data = CanvasDataFormat.records_statistics_data_format(group_records)
        return data

    @staticmethod
    def get_records_by_time_department(request_user, department_id, time):
        '''get records by time and department
        Return
        ------
        records: dict
        {
            'campus_records': QuerySet([])
            'off_campus_records':QuerySet([])
        }
        '''
        current_year = datetime.now().year
        records = {
            'campus_records': Record.objects.none(),
            'off_campus_records': Record.objects.none()
        }
        start_year = current_year
        end_year = current_year
        if time is not None:
            start_year = time['start']
            end_year = time['end']
        if start_year > end_year:
            raise BadRequest("错误的参数")
        campus_records = Record.objects.filter(
            campus_event__isnull=False,
            campus_event__time__range=(
                make_aware(datetime(start_year, 1, 1)),
                make_aware(datetime(end_year + 1, 1, 1))))
        off_campus_records = Record.objects.filter(
            off_campus_event__isnull=False,
            off_campus_event__time__range=(
                make_aware(datetime(start_year, 1, 1)),
                make_aware(datetime(end_year + 1, 1, 1))))
        departments = Department.objects.filter(id=department_id)
        if departments:
            department = departments[0]
            if request_user.is_school_admin:
                if department.name == '大连理工大学':
                    records['campus_records'] = campus_records
                    records['off_campus_records'] = off_campus_records
                else:
                    records['campus_records'] = campus_records.filter(
                        user__administrative_department=department)
                    records['off_campus_records'] = off_campus_records.filter(
                        user__administrative_department=department)
            elif request_user.check_department_admin(department):
                records['campus_records'] = campus_records.filter(
                    user__administrative_department=department)
                records['off_campus_records'] = off_campus_records.filter(
                    user__administrative_department=department)
        return records

    @classmethod
    def coverage_statistics(cls, context):
        '''to get coverage statistics data'''

    @classmethod
    def training_hours_statistics(cls, context):
        '''to get training hours statistics data'''


class TeachersGroupService:
    '''group teachers data'''

    @classmethod
    def teachers_statistics_group_dispatch(cls, users, group_by, count_only):
        ''' dispatch group_by function by group_by

        Parameters:
        ----------
        users: QuerySet
        group_by: int
        count_only: boolean
        '''
        group_by_handler = {
            EnumData.BY_TECHNICAL_TITLE: cls.group_users_by_technical_title,
            EnumData.BY_HIGHEST_DEGREE: (
                cls.group_users_by_education_background),
            EnumData.BY_AGE_DISTRIBUTION: cls.group_users_by_age,
            EnumData.BY_DEPARTMENT: cls.group_users_by_department
        }
        if group_by not in group_by_handler:
            raise BadRequest("错误的参数")
        return group_by_handler[group_by](users, count_only=count_only)

    @staticmethod
    def group_users_by_technical_title(users, count_only=False):
        '''
        Return
        ------
        group_users: dict
        {
            '教授': [USER_A, USER_B],
        } for count_only=False
        or
        {
            '教授': 3,
        } for count_only=True
        '''
        title_list = EnumData.TITLE_LABEL
        if count_only:
            group_users = {x: 0 for x in title_list}
            users = users.filter(
                technical_title__in=title_list).values(
                    'technical_title').annotate(num=Count('technical_title'))
            for user in users:
                group_users[user['technical_title']] = user['num']
        else:
            group_users = {
                x: get_user_model().objects.none() for x in title_list}
            for _, title in enumerate(title_list):
                group_users[title] = users.filter(technical_title=title)
        return group_users

    @staticmethod
    def group_users_by_education_background(users, count_only=False):
        '''
        Return
        ------
        group_users: dict
        {
            '本科毕业': [USER_A, USER_B],
        } for count_only=False
        or
        {
            '本科毕业': 3,
        } for count_only=True
        '''
        education_background_list = EnumData.EDUCATION_BACKGROUD_LABEL
        if count_only:
            group_users = {x: 0 for x in education_background_list}
            users = users.filter(
                education_background__in=education_background_list).values(
                    'education_background').annotate(
                        num=Count('education_background'))
            for user in users:
                group_users[user['education_background']] = user['num']
        else:
            group_users = {
                x: (
                    get_user_model().objects.none()
                ) for x in education_background_list}
            for _, degree in enumerate(education_background_list):
                group_users[degree] = users.filter(
                    education_background=degree)
        return group_users

    @staticmethod
    def group_users_by_department(users, count_only=False):
        '''
        Return
        ------
        group_users: dict
        {
            '创新学院': [USER_A, USER_B],
        } for count_only=False
        or
        {
            '创新学院': 3,
        } for count_only=True
        '''
        department_list = list(
            DepartmentService.get_top_level_departments().values_list('name'))
        department_list = [x[0] for x in department_list]
        if count_only:
            group_users = {x: 0 for x in department_list}
            users = (
                users.filter(
                    administrative_department__name__in=department_list)
                .values('administrative_department__name')
                .annotate(num=Count('id'))
            )
            for user in users:
                group_users[user['administrative_department__name']] = (
                    user['num']
                )
        else:
            group_users = {
                x: get_user_model().objects.none() for x in department_list}
            for _, degree in enumerate(department_list):
                group_users[degree] = users.filter(
                    administrative_department__name=degree)
        return group_users

    @staticmethod
    def group_users_by_age(users, count_only=False):
        '''
        Return
        ------
        group_users: dict
        {
            '35岁及以下': [USER_A, USER_B],
        } for count_only=False
        or
        {
            '35岁及以下': 3,
        } for count_only=Truerecords
        '''
        age_list = ((0, 35), (36, 45), (46, 55), (56, 1000))
        label_list = EnumData.AGE_LABEL
        group_users = {}
        if count_only:
            for index, value in enumerate(age_list):
                group_users[label_list[index]] = users.filter(
                    age__range=value).count()
        else:
            for index, value in enumerate(age_list):
                group_users[label_list[index]] = users.filter(age__range=value)
        return group_users


class RecordsGroupService:
    '''group records data'''

    @classmethod
    def records_statistics_group_dispatch(cls, records, group_by, count_only):
        ''' dispatch group_by function by group_by

        Parameters:
        ----------
        records: QuerySet
        group_by: int
        count_only: boolean
        '''
        group_by_handler = {
            EnumData.BY_TECHNICAL_TITLE: cls.group_records_by_technical_title,
            EnumData.BY_AGE_DISTRIBUTION: cls.group_records_by_age,
            EnumData.BY_DEPARTMENT: cls.group_records_by_department
        }
        if group_by not in group_by_handler:
            raise BadRequest("错误的参数")
        return group_by_handler[group_by](records, count_only=count_only)

    @staticmethod
    def group_records_by_technical_title(records, count_only=False):
        '''
        Return
        ------
        group_records: dict
        {
            '教授': [RECORD_A, RECORD_B],
        } for count_only=False
        or
        {
            '教授': 3,
        } for count_only=True
        '''
        title_list = EnumData.TITLE_LABEL
        if count_only:
            group_records = {x: 0 for x in title_list}
            records = records.filter(
                user__technical_title__in=title_list).values(
                    'user__technical_title').annotate(num=Count('user'))
            for record in records:
                group_records[record['user__technical_title']] = record['num']
        else:
            group_records = {x: Record.objects.none() for x in title_list}
            for _, title in enumerate(title_list):
                group_records[title] = records.filter(
                    user__technical_title=title)
        return group_records

    @staticmethod
    def group_records_by_department(records, count_only=False):
        '''
        Return
        ------
        group_records: dict
        {
            '创新学院': [RECORD_A, RECORD_B],
        } for count_only=False
        or
        {
            '创新学院': 3,
        } for count_only=True
        '''
        department_list = list(
            DepartmentService.get_top_level_departments().values_list('name'))
        department_list = [x[0] for x in department_list]
        if count_only:
            group_records = {x: 0 for x in department_list}
            records = (
                records.filter(
                    user__administrative_department__name__in=department_list)
                .values('user__administrative_department__name')
                .annotate(num=Count('id'))
            )
            for record in records:
                group_records[
                    record['user__administrative_department__name']] =\
                    record['num']
        else:
            group_records = {
                x: Record.objects.none() for x in department_list}
            for _, degree in enumerate(department_list):
                group_records[degree] = records.filter(
                    user__administrative_department__name=degree)
        return group_records

    @staticmethod
    def group_records_by_age(records, count_only=False):
        '''
        Return
        ------
        group_records: dict
            {
                '35岁及以下': [RECORD_A, RECORD_B]
            } for count_only=False
            or
            {
                '35岁及以下': 3
            } for count_only=True
        '''
        age_list = ((0, 35), (36, 45), (46, 55), (56, 1000))
        label_list = EnumData.AGE_LABEL
        group_records = {}
        if count_only:
            for index, value in enumerate(age_list):
                group_records[label_list[index]] = records.filter(
                    user__age__range=value).count()
        else:
            for index, value in enumerate(age_list):
                group_records[label_list[index]] = records.filter(
                    user__age__range=value)
        return group_records


class CanvasDataFormat:
    '''format data for canvas'''

    @staticmethod
    def records_statistics_data_format(group_records):
        ''' format records statistics data

        Parameters:
        ----------
        group_records: dict
            {
                'campus_records': dict
                'off_campus_records': dict
            }
        '''
        data = {
            'label': [],
            'group_by_data': [
                {
                    'seriesNum': 0,
                    'seriesName': '校内培训',
                    'data': []
                },
                {
                    'seriesNum': 1,
                    'seriesName': '校外培训',
                    'data': []
                }
            ]
        }
        sorted_campus_records = sorted(
            group_records['campus_records'].items(), key=lambda x: x[0])
        data['label'] = [x[0] for x in sorted_campus_records]
        data['group_by_data'][0]['data'] = (
            [x[1] for x in sorted_campus_records]
        )
        sorted_off_campus_records = sorted(
            group_records['off_campus_records'].items(),
            key=lambda x: x[0]
        )
        data['group_by_data'][1]['data'] = (
            [x[1] for x in sorted_off_campus_records]
        )
        return data

    @staticmethod
    def teachers_statistics_data_format(group_users):
        '''format statistics data

        Parameters:
        ----------
        group_users: dict
        '''
        data = {
            'label': [],
            'group_by_data': [
                {
                    'seriesNum': 0,
                    'seriesName': '专任教师',
                    'data': []
                }
            ]
        }
        data['label'] = group_users.keys()
        data['group_by_data'][0]['data'] = group_users.values()
        return data


class CanvasOptionsService:
    '''provide canvas options service'''

    @staticmethod
    def tuple_to_dict_list(data):
        '''return a data dict list'''
        return [{'type': type_num, 'name': name, 'key': key_name} for
                type_num, name, key_name in data]

    @classmethod
    def get_canvas_options(cls):
        '''return a data graph select dictionary'''
        statistics_type = [
            {'type': EnumData.TEACHERS_STATISTICS,
             'name': '教职工人数统计',
             'key': 'TEACHERS_STATISTICS',
             'subOption': cls.tuple_to_dict_list(
                 EnumData.TEACHERS_GROUPING_CHOICES)},
            {'type': EnumData.RECORDS_STATISTICS,
             'name': '培训人数统计',
             'key': 'RECORDS_STATISTICS',
             'subOption': cls.tuple_to_dict_list(
                 EnumData.TRAINEE_GROUPING_CHOICES)},
            {'type': EnumData.FULL_TIME_TEACHER_TRAINED_COVERAGE,
             'name': '专任教师培训覆盖率统计',
             'key': 'FULL_TIME_TEACHER_TRAINED_COVERAGE',
             'subOption': cls.tuple_to_dict_list(
                 EnumData.TRAINEE_GROUPING_CHOICES)},
            {'type': EnumData.TRAINING_HOURS_WORKLOAD_STATISTICS,
             'name': '培训学时与工作量统计',
             'key': 'TRAINING_HOURS_WORKLOAD_STATISTICS',
             'subOption': cls.tuple_to_dict_list(
                 EnumData.TRAINING_HOURS_GROUPING_CHOICES)}
        ]
        return statistics_type
