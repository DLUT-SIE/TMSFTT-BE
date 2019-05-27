'''培训学时与工作量统计模块'''
from django.db.models import (Count, Sum, F)
from data_warehouse.services.coverage_statistics_service import (
    CoverageStatisticsService
)
from auth.services import UserService
from training_record.models import Record


class TrainingHoursStatisticsService:
    '''培训学时与工作量统计服务'''
    @staticmethod
    def get_training_hours_data(user, start_time, end_time):
        '''返回院系的培训学时数据
        Parameters
        ------
        user: User
            当前登录的用户，必须为管理员。
            若为校级管理员，则导出所有T3院系的数据，若为院系管理员，则导出该部门的数据。
        start_time: datetime
            统计范围的开始时间
        end_time: datetime
            统计范围的结束时间

        Returns
        ------
        list of dict
            {
                key1: department,
                    部门名称
                key2: total_users,
                    学院总人数
                key3: total_coveraged_users,
                    在指定时间范围内存在培训记录的总人数
                key3: total_hours,
                    总培训学时
            }
        '''
        department_id = None
        if user.is_department_admin:
            department_id = user.administrative_department.id
        tmp_records = CoverageStatisticsService.get_training_records(
            user, department_id=department_id,
            start_time=start_time, end_time=end_time)
        # filter departments with T3 type.
        tmp_records = tmp_records.filter(
            user__administrative_department__department_type='T3')
        record_ids = tmp_records.values_list('id', flat=True)
        # Because tmp_records do not support following operations,
        # we need to fetch all records from Record.objects again.
        records = Record.objects.filter(id__in=record_ids)
        records_groupby_department = (
            records.values('user__administrative_department__name')
            .annotate(
                total_hours=Sum(
                    'campus_event__num_hours',
                    field=F('campus_event__num_hours')
                    + F('off_campus_event__num_hours')
                ),
                total_coveraged_users=Count('user', distinct=True)
            )
        )
        data = []
        for item in records_groupby_department:
            data.append(
                {
                    'department': item[
                        'user__administrative_department__name'],
                    'total_hours': item['total_hours'],
                    'total_coveraged_users': item['total_coveraged_users'],
                    'total_users': UserService.get_full_time_teachers().filter(
                        administrative_department__name=item[
                            'user__administrative_department__name']
                    ).count()
                }
            )
        return data
