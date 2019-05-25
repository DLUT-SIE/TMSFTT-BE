'''Provide services of data aggregate.'''
from django.utils.timezone import now
from django.contrib.auth import get_user_model
from django.db.models import Count
from django.utils.timezone import datetime, make_aware

from auth.models import (Department, User)
from auth.services import DepartmentService
from data_warehouse.services.user_core_statistics_service import (
    UserCoreStatisticsService
)
from data_warehouse.services.school_core_statistics_service import (
    SchoolCoreStatisticsService
)
from data_warehouse.services.user_ranking_service import (
    UserRankingService
)
from data_warehouse.services.workload_service import (
    WorkloadCalculationService
)
from data_warehouse.services.coverage_statistics_service import (
    CoverageStatisticsService)
from data_warehouse.services.table_export_service import TableExportService
from data_warehouse.services.campus_event_feedback_service import (
    CampusEventFeedbackService
)
from data_warehouse.decorators.context_params_check_decorators import (
    admin_required)
from data_warehouse.serializers import (
    CoverageStatisticsSerializer,
    TrainingFeedbackSerializer
)
from data_warehouse.consts import EnumData
from infra.exceptions import BadRequest
from training_record.models import Record
from training_program.models import Program


class AggregateDataService:
    '''provide services for getting data'''
    WORKLOAD_FILE_NAME_TEMPLATE = '{}至{}教师工作量导出表.xls'
    TABLE_NAME_STAFF = 1
    TABLE_NAME_TEACHER = 2
    TABLE_NAME_TRAINING_SUMMARY = 3
    TABLE_NAME_COVERAGE_SUMMARY = 4
    TABLE_NAME_TRAINING_HOURS_SUMMARY = 5
    TABLE_NAME_TRAINING_FEEDBACK = 6
    TABLE_NAME_WORKLOAD_CALCULATION = 7

    TABLE_NAME_CHOICES = {
        TABLE_NAME_STAFF: '教职工表',
        TABLE_NAME_TEACHER: '专任教师表',
        TABLE_NAME_TRAINING_SUMMARY: '培训总体情况表',
        TABLE_NAME_COVERAGE_SUMMARY: '专任教师培训覆盖率表',
        TABLE_NAME_TRAINING_HOURS_SUMMARY: '培训学时与工作量表',
        TABLE_NAME_TRAINING_FEEDBACK: '培训反馈表',
        TABLE_NAME_WORKLOAD_CALCULATION: '工作量计算表'
    }

    # 校验http请求参数的序列化器配置
    TABLE_SERIALIZERS_CHOICES = {
        TABLE_NAME_COVERAGE_SUMMARY: CoverageStatisticsSerializer,
        TABLE_NAME_TRAINING_FEEDBACK: TrainingFeedbackSerializer
    }

    TITLES = (
        '教授', '副教授', '讲师', '助教', '教授级工程师',
        '高级工程师', '工程师', '研究员', '副研究员', '助理研究员')

    @classmethod
    def dispatch(cls, method_name, context):
        '''to call a specific service for getting data'''
        available_method_list = (
            'teachers_statistics',
            'records_statistics',
            'coverage_statistics',
            'school_summary',
            'personal_summary',
            'table_export'
        )
        handler = getattr(cls, method_name, None)
        if method_name not in available_method_list or handler is None:
            raise BadRequest("错误的参数")
        return handler(context)

    @staticmethod
    def school_summary(_):
        '''Populate an overview statistics for the system.'''
        res = {
            'events_statistics': (
                SchoolCoreStatisticsService.get_events_statistics()
            ),
            'records_statistics': (
                SchoolCoreStatisticsService.get_records_statistics()
            ),
            'department_records_statistics': (
                SchoolCoreStatisticsService.get_department_records_statistics()
            ),
            'monthly_added_records_statistics': (
                SchoolCoreStatisticsService
                .get_monthly_added_records_statistics()
            )
        }
        return res

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
        group_users = cls.get_group_users(context)
        data = CanvasDataFormater.format_teachers_statistics_data(group_users)
        return data

    @classmethod
    def get_group_users(cls, context):
        '''get group users data'''
        group_by = context.get('group_by', '')
        department_id = context.get('department_id', '')
        if not (group_by.isdigit() and department_id.isdigit()):
            raise BadRequest("错误的参数")
        group_by = int(group_by)
        department_id = int(department_id)
        if department_id == 0:
            department_id = Department.objects.get(name='大连理工大学').id
        users = cls.get_users_by_department(
            context['request'].user, department_id)
        users = users.filter(
            teaching_type__in=('专任教师', '实验技术')
        )
        group_users = TeachersGroupService.teachers_statistics_group_dispatch(
            users, group_by, True)
        return group_users

    @staticmethod
    def get_users_by_department(request_user, department_id):
        '''get users objects by department.
        Parameters:
        ----------
        request_user: User
        department_id: int

        Return: QuerySet<User>
        '''
        queryset = User.objects.all().select_related(
            'administrative_department')
        departments = Department.objects.filter(id=department_id)
        if not departments:
            return User.objects.none()
        department = departments[0]
        if request_user.is_school_admin:
            if department.name == '大连理工大学':
                return queryset
            return queryset.filter(
                administrative_department__id=department.id)
        if request_user.check_department_admin(department):
            return queryset.filter(
                administrative_department__id=department.id)
        return User.objects.none()

    @classmethod
    def records_statistics(cls, context):
        ''' get records statistics data'''
        group_records = cls.get_group_records(context)
        data = CanvasDataFormater.format_records_statistics_data(group_records)
        return data

    @classmethod
    def get_group_records(cls, context):
        '''get group records data'''
        group_by = context.get('group_by', '')
        start_year = context.get('start_year', str(datetime.now().year))
        end_year = context.get('end_year', str(datetime.now().year))
        department_id = context.get('department_id', '')
        if not (group_by.isdigit() and start_year.isdigit() and
                end_year.isdigit() and department_id.isdigit()):
            raise BadRequest("错误的参数")
        group_by = int(group_by)
        start_year = int(start_year)
        end_year = int(end_year)
        department_id = int(department_id)
        if department_id == 0:
            department_id = Department.objects.get(name='大连理工大学').id
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
        return group_records

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
        queryset = Record.objects.select_related(
            'campus_event', 'off_campus_event', 'user').filter(
                user__teaching_type__in=('专任教师', '实验技术')
            )
        campus_records = queryset.filter(
            campus_event__isnull=False,
            campus_event__time__range=(
                make_aware(datetime(start_year, 1, 1)),
                make_aware(datetime(end_year + 1, 1, 1))))
        off_campus_records = queryset.filter(
            off_campus_event__isnull=False,
            off_campus_event__time__range=(
                make_aware(datetime(start_year, 1, 1)),
                make_aware(datetime(end_year + 1, 1, 1))))
        departments = Department.objects.filter(id=department_id)
        if not departments:
            return records
        department = departments[0]
        if request_user.is_school_admin:
            if department.name == '大连理工大学':
                records['campus_records'] = campus_records
                records['off_campus_records'] = off_campus_records
            else:
                records['campus_records'] = campus_records.filter(
                    user__administrative_department__id=department.id)
                records['off_campus_records'] = off_campus_records.filter(
                    user__administrative_department__id=department_id)
        elif request_user.check_department_admin(department):
            records['campus_records'] = campus_records.filter(
                user__administrative_department__id=department.id)
            records['off_campus_records'] = off_campus_records.filter(
                user__administrative_department__id=department.id)
        return records

    @classmethod
    def table_export(cls, context):
        '''处理表格导出相关的请求'''
        handlers = {
            cls.TABLE_NAME_TRAINING_HOURS_SUMMARY: (
                'table_training_hours_statistics'),
            cls.TABLE_NAME_COVERAGE_SUMMARY: 'table_coverage_statistics',
            cls.TABLE_NAME_TRAINING_SUMMARY: 'table_trainee_statistics',
            cls.TABLE_NAME_TRAINING_FEEDBACK: 'table_training_feedback',
            cls.TABLE_NAME_WORKLOAD_CALCULATION: 'table_workload_calculation'
        }
        request = context.get('request', None)
        if request is None:
            raise BadRequest('错误的参数。')
        table_type = int(request.GET.get('table_type'))
        handler = handlers.get(table_type, None)
        if handler is None:
            raise BadRequest('未定义的表类型。')
        handler_method = getattr(cls, handler, None)
        return handler_method(context)

    @classmethod
    def training_hours_statistics(cls, context):
        '''to get training hours statistics data'''

    @classmethod
    def table_trainee_statistics(cls, context):
        '''培训学时与工作量'''

    @classmethod
    def coverage_statistics(cls, context):
        '''get canvas coverage statistics data'''
        group_data = cls.get_group_coverage_data(context)
        data = CanvasDataFormater.format_coverage_statistics_data(group_data)
        return data

    @classmethod
    def get_group_coverage_data(cls, context):
        '''get group coverage data'''
        group_by = context.get('group_by', '')
        start_year = context.get('start_year', str(datetime.now().year))
        end_year = context.get('end_year', str(datetime.now().year))
        department_id = context.get('department_id', '')
        program_id = context.get('program_id', '')
        if not (group_by.isdigit() and start_year.isdigit() and
                end_year.isdigit() and department_id.isdigit() and
                program_id.isdigit()):
            raise BadRequest("错误的参数")
        department_id = None if department_id == '0' else int(department_id)
        program_id = None if program_id == '0' else int(program_id)
        start_time = make_aware(
            datetime.strptime(start_year + '-1-1', '%Y-%m-%d'))
        end_year = str(int(end_year) + 1)
        end_time = make_aware(
            datetime.strptime(end_year + '-1-1', '%Y-%m-%d'))
        group_by = int(group_by)
        records = CoverageStatisticsService.get_traning_records(
            context['request'].user, program_id, department_id,
            start_time, end_time)
        users_qs = User.objects.filter(id__in=records.values_list(
            'user', flat=True).distinct())
        group_by_handler = {
            EnumData.BY_TECHNICAL_TITLE: (
                CoverageStatisticsService.groupby_titles),
            EnumData.BY_AGE_DISTRIBUTION: (
                CoverageStatisticsService.groupby_ages),
            EnumData.BY_DEPARTMENT: (
                CoverageStatisticsService.groupby_departments)
        }
        if group_by not in group_by_handler:
            raise BadRequest("错误的参数")
        group_users = group_by_handler[group_by](users_qs)
        return group_users

    @classmethod
    def table_workload_calculation(cls, context):
        '''工作量计算表格'''
        # 生成excel文件
        request = context.get('request', None)
        data = request.GET
        start_time = data.get('start_time')
        end_time = data.get('end_time')

        if end_time is None:
            end_time = now()
        if start_time is None:
            start_time = end_time.replace(year=end_time.year - 1,
                                          month=12, day=31, hour=16, minute=0,
                                          second=0)

        workload_dict = (
            WorkloadCalculationService.calculate_workload_by_query(
                administrative_department=data.get(
                    'administrative_department'),
                start_time=start_time,
                end_time=end_time,
                teachers=data.get('teachers')
            )
        )
        file_path = (
            WorkloadCalculationService.generate_workload_excel_from_data(
                workload_dict=workload_dict
            )
        )

        # 拼接文件名
        file_name = cls.FILE_NAME_TEMPLATE.format(
            start_time.strftime('%Y-%m-%d'), end_time.strftime('%Y-%m-%d'))
        return file_path, file_name

    @classmethod
    @admin_required()
    def table_coverage_statistics(cls, context):
        '''专任教师培训覆盖率表格统计'''
        request = context.get('request', None)
        program_id = context.get('program_id', None)
        start_time = context.get('start_time', None)
        end_time = context.get('end_time', None)
        department_id = context.get('department_id', None)

        records = CoverageStatisticsService.get_traning_records(
            request.user, program_id, department_id, start_time, end_time)
        users_qs = User.objects.filter(id__in=records.values_list(
            'user', flat=True).distinct())
        group_users_by_ages = CoverageStatisticsService.groupby_ages(users_qs)
        group_users_by_depts = CoverageStatisticsService.groupby_departments(
            users_qs)
        group_users_by_titles = CoverageStatisticsService.groupby_titles(
            users_qs,
            cls.TITLES
            )
        grouped_records = {
            'ages': group_users_by_ages,
            'titles': group_users_by_titles,
            'departments': group_users_by_depts
        }
        file_path = TableExportService.export_traning_coverage_summary(
            grouped_records)
        return file_path, '专任教师培训覆盖率.xls'

    @classmethod
    @admin_required()
    def table_training_feedback(cls, context):
        '''培训记录反馈导出'''
        request = context.get('request')
        program_id = context.get('program_id', None)
        deparment_id = context.get('department_id', None)
        if not (program_id or deparment_id):
            raise BadRequest('必须给定部门ID或者项目ID')
        elif not deparment_id:
            program_ids = [program_id]
        else:
            program_ids = Program.objects.filter(
                department_id=deparment_id).values_list('id', flat=True)
        feedbacks = CampusEventFeedbackService.get_feedbacks(
            request.user, program_ids)
        # prepare data to be written in excel.
        data = []
        for feedback in feedbacks:
            data.append(
                {
                    'program_name': feedback.record.campus_event.program.name,
                    'campus_event_name': feedback.record.campus_event.name,
                    'feedback_content': feedback.content,
                    'feedback_time': (
                        feedback.create_time.strftime('%Y-%m-%d %H:%M:%S')
                        ),
                    'feedback_user_name': feedback.record.user.first_name,
                    'feedback_user_email': feedback.record.user.email,
                    'feedback_user_department': (
                        feedback.record.user.administrative_department.name)
                }
            )
        file_path = TableExportService.export_training_feedback(data)
        return file_path, '培训反馈表.xls'


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
            total_count = users.count()
            group_users = {x: 0 for x in title_list}
            users = users.filter(
                technical_title__in=title_list).values(
                    'technical_title').annotate(count=Count('technical_title'))
            sum_count = 0
            for user in users:
                sum_count += user['count']
                group_users[user['technical_title']] = user['count']
            group_users['其他'] = total_count - sum_count
        else:
            group_users = {
                x: get_user_model().objects.none() for x in title_list}
            for _, title in enumerate(title_list):
                group_users[title] = users.filter(technical_title=title)
            group_users['其他'] = users.exclude(technical_title__in=title_list)
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
                        count=Count('education_background'))
            for user in users:
                group_users[user['education_background']] = user['count']
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
                .annotate(count=Count('id'))
            )
            for user in users:
                group_users[user['administrative_department__name']] = (
                    user['count']
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
            total_count = records.count()
            group_records = {x: 0 for x in title_list}
            records = records.filter(
                user__technical_title__in=title_list).values(
                    'user__technical_title').annotate(count=Count('user'))
            sum_count = 0
            for record in records:
                sum_count += record['count']
                group_records[
                    record['user__technical_title']] = record['count']
            group_records['其他'] = total_count - sum_count
        else:
            group_records = {x: Record.objects.none() for x in title_list}
            for _, title in enumerate(title_list):
                group_records[title] = records.filter(
                    user__technical_title=title)
            group_records['其他'] = records.exclude(
                user__technical_title__in=title_list)
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
            DepartmentService.get_top_level_departments().values_list(
                'name', flat=True))
        if count_only:
            group_records = {x: 0 for x in department_list}
            records = (
                records.filter(
                    user__administrative_department__name__in=department_list)
                .values('user__administrative_department__name')
                .annotate(count=Count('id'))
            )
            for record in records:
                group_records[
                    record['user__administrative_department__name']] =\
                    record['count']
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


class CanvasDataFormater:
    '''format data for canvas'''

    @staticmethod
    def format_records_statistics_data(group_records):
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
        random_key = list(group_records['campus_records'].keys())[0]
        labels = [
            EnumData.AGE_LABEL,
            EnumData.EDUCATION_BACKGROUD_LABEL,
            EnumData.TITLE_LABEL
        ]
        for label in labels:
            if random_key in label:
                data['label'] = label
                break
        if not data['label']:
            data['label'] = list(group_records['campus_records'].keys())
        for label in data['label']:
            data['group_by_data'][0]['data'].append(
                group_records['campus_records'][label])
            data['group_by_data'][1]['data'].append(
                group_records['off_campus_records'][label])
        return data

    @staticmethod
    def format_teachers_statistics_data(group_users):
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
        if not group_users:
            return data
        random_key = list(group_users.keys())[0]
        labels = [
            EnumData.AGE_LABEL,
            EnumData.EDUCATION_BACKGROUD_LABEL,
            EnumData.TITLE_LABEL
        ]
        for label in labels:
            if random_key in label:
                data['label'] = label
                break
        if not data['label']:
            data['label'] = list(group_users.keys())
        for label in data['label']:
            data['group_by_data'][0]['data'].append(group_users[label])
        return data

    @staticmethod
    def format_coverage_statistics_data(group_users):
        '''format coverage statistics data

        Parameters:
        ----------
        group_users: list of dict
            [
                {
                    "age_range" or "title" or "department": "35岁及以下",
                    "coverage_count": 0,
                    "total_count": 965
                }
            ]
        '''
        data = {
            'label': [],
            'group_by_data': [
                {
                    'seriesNum': 0,
                    'seriesName': '覆盖人数',
                    'data': []
                },
                {
                    'seriesNum': 1,
                    'seriesName': '未覆盖人数',
                    'data': []
                }
            ]
        }
        if not bool(group_users):
            return data
        interest_label = None
        if 'age_range' in group_users[0].keys():
            label_key = 'age_range'
            interest_label = EnumData.AGE_LABEL
        elif 'department' in group_users[0].keys():
            label_key = 'department'
            interest_label = list(
                DepartmentService
                .get_top_level_departments()
                .values_list('name', flat=True))
        else:
            label_key = 'title'
            interest_label = EnumData.TITLE_LABEL
        for user in group_users:
            if interest_label and user[label_key] not in interest_label:
                continue
            data['label'].append(user[label_key])
            data['group_by_data'][0]['data'].append(user['coverage_count'])
            data['group_by_data'][1]['data'].append(
                user['total_count'] - user['coverage_count'])
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
            {'type': EnumData.COVERAGE_STATISTICS,
             'name': '专任教师培训覆盖率统计',
             'key': 'COVERAGE_STATISTICS',
             'subOption': cls.tuple_to_dict_list(
                 EnumData.TRAINEE_GROUPING_CHOICES)},
            {'type': EnumData.TRAINING_HOURS_WORKLOAD_STATISTICS,
             'name': '培训学时与工作量统计',
             'key': 'TRAINING_HOURS_WORKLOAD_STATISTICS',
             'subOption': cls.tuple_to_dict_list(
                 EnumData.TRAINING_HOURS_GROUPING_CHOICES)}
        ]
        return statistics_type
