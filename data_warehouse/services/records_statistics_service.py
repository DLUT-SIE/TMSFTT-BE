'''provide records statistics relevant methods'''
from django.db.models import Count

from data_warehouse.consts import EnumData
from auth.models import Department
from auth.services import DepartmentService
from infra.exceptions import BadRequest
from training_record.models import Record


class RecordsStatisticsService:
    '''get records statistics data'''

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

    @staticmethod
    def get_records_by_time_department(request_user, department_id, time):
        '''get records by time and department
        Parameters
        ----------
        request_user: User object
        department_id: int
        time: dict
            {
                'start_time': datetime
                'end_time': datetime
            }

        Return
        ------
        records: dict
        {
            'campus_records': QuerySet([])
            'off_campus_records':QuerySet([])
        }
        '''
        records = {
            'campus_records': Record.objects.none(),
            'off_campus_records': Record.objects.none()
        }
        start_time = time['start_time']
        end_time = time['end_time']
        if start_time > end_time:
            raise BadRequest("错误的参数")
        queryset = Record.objects.select_related(
            'campus_event', 'off_campus_event', 'user').filter(
                user__teaching_type__in=('专任教师', '实验技术')
            )
        campus_records = queryset.filter(
            campus_event__isnull=False,
            campus_event__time__range=(start_time, end_time)
            )
        off_campus_records = queryset.filter(
            off_campus_event__isnull=False,
            off_campus_event__time__range=(start_time, end_time)
            )
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
