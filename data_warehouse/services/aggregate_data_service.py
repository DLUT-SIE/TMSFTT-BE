'''Provide services of data aggregate.'''
from django.utils.timezone import now, localtime
from django.utils.timezone import datetime

from auth.models import Department, User
from infra.exceptions import BadRequest
from training_program.models import Program
from training_event.services import EnrollmentService
from training_event.models import CampusEvent
from training_record.models import Record

from data_warehouse.services import (
    UserCoreStatisticsService,
    TeachersStatisticsService,
    RecordsStatisticsService,
    CanvasDataFormater,
    SchoolCoreStatisticsService,
    UserRankingService,
    WorkloadCalculationService,
    CoverageStatisticsService,
    TableExportService,
    CampusEventFeedbackService,
    TrainingHoursStatisticsService
)
from data_warehouse.decorators import (
    admin_required,
)
from data_warehouse.services.training_record_service import (
    TrainingRecordService)
from data_warehouse.serializers import (
    CoverageStatisticsSerializer,
    TrainingFeedbackSerializer,
    SummaryParametersSerializer,
    TrainingHoursSerializer,
    TableTrainingRecordsSerializer,
    AttendanceSheetSerializer,
    TrainingSummarySerializer,
    EventAttendanceSummarySerializer,
    WorkloadCalculationSerializer
)
from data_warehouse.consts import EnumData


# pylint: disable=R0904
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
    TABLE_NAME_TRAINING_RECORDS = 8
    TABLE_NAME_ATTENDANCE_SHEET = 9
    TABLE_NAME_EVENT_ATTENDANCE_SUMMARY = 10

    TABLE_NAME_CHOICES = {
        TABLE_NAME_STAFF: '教职工表',
        TABLE_NAME_TEACHER: '专任教师表',
        TABLE_NAME_TRAINING_SUMMARY: '培训总体情况表',
        TABLE_NAME_COVERAGE_SUMMARY: '专任教师培训覆盖率表',
        TABLE_NAME_TRAINING_HOURS_SUMMARY: '培训学时与工作量表',
        TABLE_NAME_TRAINING_FEEDBACK: '培训反馈表',
        TABLE_NAME_WORKLOAD_CALCULATION: '工作量计算表',
        TABLE_NAME_TRAINING_RECORDS: '个人培训记录',
        TABLE_NAME_ATTENDANCE_SHEET: '签到表',
        TABLE_NAME_EVENT_ATTENDANCE_SUMMARY: '培训活动出席表',
    }

    # 校验http请求参数的序列化器配置
    TABLE_SERIALIZERS_CHOICES = {
        TABLE_NAME_COVERAGE_SUMMARY: CoverageStatisticsSerializer,
        TABLE_NAME_TRAINING_FEEDBACK: TrainingFeedbackSerializer,
        TABLE_NAME_TRAINING_HOURS_SUMMARY: TrainingHoursSerializer,
        TABLE_NAME_TRAINING_RECORDS: TableTrainingRecordsSerializer,
        TABLE_NAME_ATTENDANCE_SHEET: AttendanceSheetSerializer,
        TABLE_NAME_TRAINING_SUMMARY: TrainingSummarySerializer,
        TABLE_NAME_EVENT_ATTENDANCE_SUMMARY: EventAttendanceSummarySerializer,
        TABLE_NAME_WORKLOAD_CALCULATION: WorkloadCalculationSerializer,
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
            'training_hours_statistics',
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
        user = request.user if request else context.get('user', None)
        if not user:
            raise BadRequest('参数错误')
        serializer = SummaryParametersSerializer(data=context)
        serializer.is_valid(raise_exception=True)
        context = serializer.data
        context['request'] = request

        res = {
            'programs_statistics': (
                UserCoreStatisticsService.get_programs_statistics(
                    user, context)
            ),
            'events_statistics': (
                UserCoreStatisticsService.get_events_statistics(
                    user, context)
            ),
            'records_statistics': (
                UserCoreStatisticsService.get_records_statistics(
                    user, context)
            ),
            'competition_award_info': (
                UserCoreStatisticsService.get_competition_award_info(
                    user, context)
            ),
            'monthly_added_records': (
                UserCoreStatisticsService
                .get_monthly_added_records_statistics(user, context)
            ),
            'ranking_in_department': (
                UserRankingService
                .get_total_training_hours_ranking_in_department(user, context)
            ),
            'ranking_in_school': (
                UserRankingService
                .get_total_training_hours_ranking_in_school(user, context)
            ),
            'personal_workload': {
                'timestamp': localtime(now()),
                'workload': (
                    WorkloadCalculationService
                    .calculate_workload_by_query(teachers=[user])
                    .get(user)
                ),
            },
        }
        return res

    @classmethod
    @admin_required()
    def teachers_statistics(cls, context):
        ''' get teachers statistics data'''
        group_users = cls.get_group_users(context)
        data = CanvasDataFormater.format_teachers_statistics_data(group_users)
        return data

    @staticmethod
    def get_group_users(context):
        '''get group users data'''
        group_by = context.get('group_by', '')
        department_id = context.get('department_id', '')
        program_id = context.get('program_id', None)
        if not (group_by.isdigit() and department_id.isdigit()):
            raise BadRequest("错误的参数")
        group_by = int(group_by)
        department_id = int(department_id)
        if department_id == 0:
            department_id = Department.objects.get(name='大连理工大学').id
        users = TeachersStatisticsService.get_users_by_department(
            context['request'].user, department_id)
        users = users.filter(
            teaching_type__in=('专任教师', '实验技术')
        )
        if program_id and program_id != '0':
            program_id = int(program_id)
            events = CampusEvent.objects.filter(program=program_id)
            records = Record.objects.filter(campus_event__in=events)
            users_in_program_id = {record.user.id for record in records}
            users = users.filter(id__in=users_in_program_id)
        group_users = (
            TeachersStatisticsService.teachers_statistics_group_dispatch(
                users, group_by, count_only=True))
        return group_users

    @classmethod
    @admin_required()
    def records_statistics(cls, context):
        ''' get records statistics data'''
        group_records = cls.get_group_records(context)
        data = CanvasDataFormater.format_records_statistics_data(group_records)
        return data

    @staticmethod
    def get_group_records(context):
        '''get group records data 培训总体情况数据'''
        group_by = context.get('group_by', '')
        start_time = context.get('start_time',
                                 datetime.now().replace(year=2016))
        end_time = context.get('end_time', datetime.now())
        department_id = context.get('department_id', '')
        program_id = context.get('program_id', None)
        if not (group_by.isdigit() and department_id.isdigit()):
            raise BadRequest("错误的参数")
        group_by = int(group_by)
        department_id = int(department_id)
        if department_id == 0:
            department_id = Department.objects.get(name='大连理工大学').id
        time = {'start_time': start_time, 'end_time': end_time}
        records = RecordsStatisticsService.get_records_by_time_department(
            context['request'].user, department_id, time)
        if program_id and program_id != '0':
            program_id = int(program_id)
            records['campus_records'] = records['campus_records'].filter(
                campus_event__program=program_id)
            records['off_campus_records'] = (
                records['off_campus_records'].filter(
                    off_campus_event__isnull=True))
        group_records = {}
        group_records['campus_records'] = (
            RecordsStatisticsService.records_statistics_group_dispatch(
                records['campus_records'], group_by, True)
        )
        group_records['off_campus_records'] = (
            RecordsStatisticsService.records_statistics_group_dispatch(
                records['off_campus_records'], group_by, True)
        )
        return group_records

    @staticmethod
    def get_group_hours_data(context):
        '''get group training hours data'''
        start_time = context.get('start_time',
                                 datetime.now().replace(year=2016))
        end_time = context.get('end_time', datetime.now())
        group_data = TrainingHoursStatisticsService.get_training_hours_data(
            context['request'].user, start_time, end_time)
        return group_data

    @classmethod
    @admin_required()
    def coverage_statistics(cls, context):
        '''get canvas coverage statistics data'''
        group_data = cls.get_group_coverage_data(context)
        data = CanvasDataFormater.format_coverage_statistics_data(group_data)
        return data

    @staticmethod
    def get_group_coverage_data(context):
        '''get group coverage data'''
        group_by = context.get('group_by', '')
        start_time = context.get('start_time',
                                 datetime.now().replace(year=2016))
        end_time = context.get('end_time', datetime.now())
        department_id = context.get('department_id', '')
        program_id = context.get('program_id', '')
        if not (group_by.isdigit() and department_id.isdigit() and
                program_id.isdigit()):
            raise BadRequest("错误的参数")
        department_id = None if department_id == '0' else int(department_id)
        program_id = None if program_id == '0' else int(program_id)
        group_by = int(group_by)
        records = CoverageStatisticsService.get_training_records(
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
    @admin_required()
    def training_hours_statistics(cls, context):
        '''to get training hours statistics data'''
        group_data = cls.get_group_hours_data(context)

        data = CanvasDataFormater.format_hours_statistics_data(
            group_data)
        return data

    @classmethod
    def table_export(cls, context):
        '''处理表格导出相关的请求'''
        handlers = {
            cls.TABLE_NAME_TRAINING_HOURS_SUMMARY:
            'table_training_hours_statistics',
            cls.TABLE_NAME_COVERAGE_SUMMARY: 'table_coverage_statistics',
            cls.TABLE_NAME_TRAINING_SUMMARY: 'table_training_summary',
            cls.TABLE_NAME_TRAINING_FEEDBACK: 'table_training_feedback',
            cls.TABLE_NAME_WORKLOAD_CALCULATION: 'table_workload_calculation',
            cls.TABLE_NAME_TRAINING_RECORDS: 'table_training_records',
            cls.TABLE_NAME_TEACHER: 'table_teacher_statistics',
            cls.TABLE_NAME_ATTENDANCE_SHEET: 'attendance_sheet',
            cls.TABLE_NAME_EVENT_ATTENDANCE_SUMMARY:
            'table_event_attendance_summary',
        }
        table_type = context.get('table_type')
        handler = handlers.get(table_type, None)
        if handler is None:
            raise BadRequest('未定义的表类型。')
        handler_method = getattr(cls, handler, None)
        return handler_method(context)

    @classmethod
    @admin_required()
    def table_training_hours_statistics(cls, context):
        '''培训学时与工作量'''
        request = context.get('request')
        if not request.user.is_school_admin:
            raise BadRequest('你不是校级管理员。')
        start_time = context.get('start_time')
        end_time = context.get('end_time')
        data = TrainingHoursStatisticsService.get_training_hours_data(
            request.user, start_time, end_time)
        file_path = TableExportService.export_training_hours(data)
        __end_time = end_time if end_time is not None else now()
        __start_time = start_time if start_time is not None else now()
        __department_name = request.user.administrative_department.name
        prefix = f'{__start_time.year}至{__end_time.year}-{__department_name}'
        return file_path, f'{prefix}-培训学时与工作量表.xls'

    @classmethod
    @admin_required()
    def table_workload_calculation(cls, context):
        '''工作量计算表格'''
        # 生成excel文件
        request = context.get('request', None)
        data = request.GET
        start_time = context.get('start_time', None)
        end_time = context.get('end_time', None)
        administrative_department = None

        if end_time is None:
            end_time = now()
        if start_time is None:
            start_time = end_time.replace(year=end_time.year - 1,
                                          month=12, day=31, hour=16, minute=0,
                                          second=0)
        if not request.user.is_school_admin:
            administrative_department = request.user.administrative_department

        workload_dict = (
            WorkloadCalculationService.calculate_workload_by_query(
                administrative_department=administrative_department,
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
        file_name = cls.WORKLOAD_FILE_NAME_TEMPLATE.format(
            start_time.strftime('%Y-%m-%d'), end_time.strftime('%Y-%m-%d'))
        return file_path, file_name

    # pylint: disable=R0914
    @classmethod
    @admin_required()
    def table_coverage_statistics(cls, context):
        '''专任教师培训覆盖率表格统计'''
        request = context.get('request', None)
        program_id = context.get('program_id', None)
        start_time = context.get('start_time', None)
        end_time = context.get('end_time', None)
        department_id = context.get('department_id', None)

        records = CoverageStatisticsService.get_training_records(
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
        __department_name = (
            request.user.administrative_department
            .name if department_id is None else Department.objects.filter(
                id=department_id)[0].name
            )
        __end_time = end_time if end_time is not None else now()
        __start_time = start_time if start_time is not None else now()
        __program_name = '全部培训项目' if program_id is None else (
            Program.objects.filter(id=program_id)[0].name)
        prefix = (
            f'{__start_time.year}至{__end_time.year}-{__department_name}-'
            f'{__program_name}'
            )
        return file_path, f'{prefix}-专任教师培训覆盖率.xls'

    @classmethod
    @admin_required()
    def table_training_feedback(cls, context):
        '''培训记录反馈导出'''
        request = context.get('request')
        program_id = context.get('program_id', None)
        department_id = context.get('department_id', None)
        user = request.user
        if department_id is not None:
            department = Department.objects.filter(id=department_id)
            if not department:
                raise BadRequest('部门不存在。')
            if not (user.is_school_admin or user.check_department_admin(
                    department[0])):
                raise BadRequest('你不是该院系的管理员，无权操作。')
        if program_id:
            program_ids = [program_id]
        else:
            program_ids = Program.objects.filter(
                department_id=department_id).values_list('id', flat=True)
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
                        localtime(feedback.create_time).strftime(
                            '%Y-%m-%d %H:%M:%S')
                        ),
                    'feedback_user_name': feedback.record.user.first_name,
                    'feedback_user_email': feedback.record.user.email,
                    'feedback_user_department': (
                        feedback.record.user.administrative_department.name if
                        feedback.record.user.administrative_department else '')
                }
            )
        file_path = TableExportService.export_training_feedback(data)
        program_names = Program.objects.filter(
            id__in=program_ids).values_list('name', flat=True)[:3]
        program_names = '-'.join(program_names)
        prefix = f'{program_names}等培训项目'
        return file_path, f'{prefix}-培训反馈表.xls'

    @classmethod
    def table_training_records(cls, context):
        '''个人培训记录导出'''
        request = context.get('request')
        event_name = context['event_name']
        event_location = context['event_location']
        start_time = context['start_time']
        end_time = context['end_time']
        username = context['user__username']
        if not username:
            user = request.user
        else:
            user = User.objects.filter(username=username).first()
            if user and not (request.user.is_school_admin or (
                    request.user.check_department_admin(
                        user.department))):
                raise BadRequest('您无权查看该用户的培训记录')

        matched_records = TrainingRecordService.get_records(
            user, event_name, event_location, start_time, end_time)
        matched_records = matched_records.select_related(
            'campus_event', 'off_campus_event', 'event_coefficient')
        # prepare data to be written in excel.
        data = []
        for record in matched_records:
            data.append(
                {
                    'event_name':
                    record.campus_event.name
                    if record.campus_event else record.off_campus_event.name,
                    'event_time':
                    localtime(record.campus_event.time)
                    if record.campus_event else localtime(
                        record.off_campus_event.time),
                    'event_location':
                    record.campus_event.location
                    if record.campus_event
                    else record.off_campus_event.location,
                    'num_hours':
                    record.campus_event.num_hours
                    if record.campus_event
                    else record.off_campus_event.num_hours,
                    'create_time': localtime(record.create_time),
                    'role': record.event_coefficient.get_role_display(),
                    'status': record.get_status_display(),
                }
            )
        file_path = TableExportService.export_records_for_user(data)
        return file_path, '个人培训记录.xls'

    @classmethod
    @admin_required()
    def table_teacher_statistics(cls, context):
        '''专任教师情况表导出'''
        # adapt to @wangyang's code.
        request = context.get('request')
        user = request.user
        department_id = '0' if user.is_school_admin else str(
            user.administrative_department.id)
        context['department_id'] = department_id
        data = []
        for group_by in EnumData.GROUP_BY_LIST:
            # populate group_by params because endpoint
            # wont give us the param.
            context['group_by'] = str(group_by)
            group_users = cls.get_group_users(context)
            data.append(group_users)
        file_path = TableExportService.export_teacher_statistics(data)
        __department_name = '大连理工大学' if department_id == 0 else (
            user.administrative_department.name)
        prefix = f'{__department_name}'
        return file_path, f'{prefix}-专任教师情况表.xls'

    # pylint: disable=R0914
    @classmethod
    @admin_required()
    def table_training_summary(cls, context):
        '''培训总体情况表导出'''
        # adapt to @wangyang's code
        request = context.get('request')
        context['program_id'] = request.query_params.get('program_id', None)
        user = request.user
        department_id = '0' if user.is_school_admin else str(
            user.administrative_department.id)
        context['department_id'] = department_id
        start_time = context.get('start_time', None)
        end_time = context.get('end_time', None)
        if start_time is not None:
            context['start_year'] = str(start_time.year)
        if end_time is not None:
            context['end_year'] = str(end_time.year)
        data = []
        group_by_list = [
            EnumData.BY_DEPARTMENT, EnumData.BY_TECHNICAL_TITLE,
            EnumData.BY_AGE_DISTRIBUTION]
        for group_by in group_by_list:
            # populate group_by params because endpoint
            # wont give us the param.
            context['group_by'] = str(group_by)
            group_records = cls.get_group_records(context)
            data.append(group_records)
        file_path = TableExportService.export_training_summary(data)
        __department_name = '大连理工大学' if department_id == 0 else (
            user.administrative_department.name)
        __end_time = end_time if end_time is not None else now()
        __start_time = start_time if start_time is not None else now()
        prefix = f'{__start_time.year}至{__end_time.year}-{__department_name}'
        return file_path, f'{prefix}-培训总体情况表.xls'

    @classmethod
    def attendance_sheet(cls, context):
        '''签到表导出'''
        event_id = context.get('event_id')
        enrollments = EnrollmentService.get_enrollments(
            event_id, context={'user': context['request'].user})
        file_path = TableExportService.export_attendance_sheet(enrollments)
        return file_path, '签到表.xls'

    # pylint: disable=R0914
    @classmethod
    @admin_required()
    def table_event_attendance_summary(cls, context):
        '''培训活动出席表导出'''
        request = context.get('request')
        program_id = request.query_params.get('program_id', None)
        department_id = request.query_params.get('department_id', None)
        user = request.user
        if department_id is not None:
            department = Department.objects.filter(id=department_id)
            if not department:
                raise BadRequest('部门不存在。')
            if not (user.is_school_admin or user.check_department_admin(
                    department[0])):
                raise BadRequest('你不是该院系的管理员，无权操作。')
        start_time = context.get('start_time',
                                 localtime(now()).replace(year=2016))
        end_time = context.get('end_time', localtime(now()))
        if user.is_school_admin:
            programs = Program.objects.filter()
        elif program_id is None:
            programs = Program.objects.filter(department_id=department_id)
        else:
            programs = Program.objects.filter(id=program_id)

        file_path = TableExportService.export_event_attendance_summary(
            programs, start_time, end_time)
        __department_name = '大连理工大学' if department_id == 0 else (
            user.administrative_department.name)
        __end_time = end_time if end_time is not None else now()
        __start_time = start_time if start_time is not None else now()
        prefix = f'{__start_time.year}至{__end_time.year}-{__department_name}'
        return file_path, f'{prefix}-培训总体情况表.xls'
