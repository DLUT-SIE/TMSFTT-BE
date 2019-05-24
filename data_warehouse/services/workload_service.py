'''Provide services of workload module.'''
from itertools import chain
import tempfile

import xlwt
from django.utils.timezone import now

from training_record.models import Record
from auth.models import User


class WorkloadCalculationService:
    '''Provide workload calculation method .'''

    WORKLOAD_SHEET_NAME = '工作量汇总统计'
    WORKLOAD_SHEET_TITLE = ['序号', '学部（学院）', '教师姓名', '工作量']
    WORKLOAD_SHEET_TITLE_STYLE = ('font: bold on; '
                                  'align: wrap on, vert centre, horiz center'
                                  )

    @staticmethod
    def calculate_workload_by_query(administrative_department=None,
                                    start_time=None, end_time=None,
                                    teachers=None):
        """calculate workload by department and period

        Parameters
        ----------
        start_time: date
            查询起始时间
        end_time: date
            查询结束时间
        department: Department
            查询的学院
        teachers: list of users, optional
            可选参数，list中存储需要查询的老师，该参数与department互斥，当二者
            同时存在时，以teachers参数查询为主，department参数不生效
        Returns
        -------
        result: dict
            key 为学部老师
            values 为该老师在规定查询时间段内的工时
        """
        if end_time is None:
            end_time = now()
        if start_time is None:
            start_time = end_time.replace(month=1, day=1, hour=0, minute=0,
                                          second=0)
        if teachers is None:
            teachers = User.objects.exclude(
                administrative_department__isnull=True)
            if administrative_department is not None:
                teachers = teachers.filter(
                    administrative_department=administrative_department)
        campus_records = Record.objects.select_related(
            'event_coefficient', 'user',
            'user__administrative_department').filter(
                user__in=teachers, campus_event__time__gte=start_time,
                campus_event__time__lte=end_time)

        off_campus_records = Record.objects.select_related(
            'event_coefficient', 'user',
            'user__administrative_department').filter(
                user__in=teachers, off_campus_event__time__gte=start_time,
                off_campus_event__time__lte=end_time)
        result = {}
        for record in chain(campus_records, off_campus_records):
            user = record.user
            result.setdefault(user, 0)
            result[user] += (
                record.event_coefficient.calculate_event_workload(record)
            )

        return result

    @staticmethod
    def generate_workload_excel_from_data(workload_dict):
        """ 根据传入的工作量汇总字典生成excel

        Parameters
        ----------
        workload_dict: dict
            key 为user，value为对应user的工作量，通过调用
            calculate_workload_by_query方法获取相应字典
        Returns
        -------
        file_path: str
        """

        # 初始化excel
        workbook = xlwt.Workbook()
        worksheet = workbook.add_sheet(
            WorkloadCalculationService.WORKLOAD_SHEET_NAME)
        style = xlwt.easyxf(
            WorkloadCalculationService.WORKLOAD_SHEET_TITLE_STYLE)
        # 生成表头
        for col, title in enumerate(
                WorkloadCalculationService.WORKLOAD_SHEET_TITLE):
            worksheet.write(0, col, title, style)

        # 根据学院名排序，优化输出形式
        workload_list = sorted(
            workload_dict.items(),
            key=lambda item: item[0].administrative_department.name)
        # 写数据
        for row, teacher in enumerate(workload_list):
            worksheet.write(row + 1, 0, row + 1)
            worksheet.write(row + 1, 1,
                            teacher[0].administrative_department.name)
            worksheet.write(row + 1, 2, teacher[0].first_name)
            worksheet.write(row + 1, 3, teacher[1])

        _, file_path = tempfile.mkstemp()

        workbook.save(file_path)
        return file_path
