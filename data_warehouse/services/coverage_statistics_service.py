'''培训覆盖率服务'''
from django.utils.timezone import now
from django.db.models import Count
from training_record.models import Record
from training_program.models import Program
from auth.models import User, Department
from auth.services import DepartmentService
from infra.exceptions import BadRequest


class CoverageStatisticsService:
    '''培训覆盖率统计服务'''
    AGES = (
        ('35岁及以下', [0, 35]), ('36-45岁', [36, 45]),
        ('46-55岁', [46, 55]), ('56岁及以上', [56, 150]))

    @staticmethod
    def teacher_coverage():
        '''专任教师培训覆盖率统计'''

    @staticmethod
    def groupby_ages(users_qs):
        '''按照年龄段分组

        Parameters
        -------
        users_qs: QuerySet
            待分组的User查询集

        Returns
        ------
        list of dict
            按年龄分组后的结果，list包含的元素dict定义为： {
                age_range: string,
                    年龄段，例如 35岁及以下。
                coverage_count: int,
                    参数users_qs包含的用户中，该年龄段对应的用户人数。
                total_count: int
                    系统里该年龄段对应的用户总人数。
            }
        '''
        data = []
        for age_range in CoverageStatisticsService.AGES:
            label = age_range[0]
            data.append(
                {
                    'age_range': label,
                    'coverage_count': users_qs.filter(
                        age__range=age_range[1]).count(),
                    'total_count': User.objects.filter(
                        age__range=age_range[1]).count()
                }
            )
        return data

    @staticmethod
    def groupby_titles(users_qs, interest_titles=None, other_label='其他'):
        '''按照职称分组

        Parameters
        -------
        users_qs: QuerySet
            待分组的User查询集
        interest_titles: tuple or list
            职称的显式分组列表，不在该列表中的职称会被分组为other_label。
            为None，则每个职称单独成组。
        other_label: string
            不在interest_titles的职称会被归类为该组。
        Returns
        ------
        list of dict
            按职称分组后的结果，list包含的元素dict定义为： {
                title: string,
                coverage_count: int,
                    参数users_qs包含的用户中，该职称对应的用户人数。
                total_count: int
                    系统里该职称对应的用户总人数。
            }
        '''
        data = []
        coverage_titles = users_qs.values('technical_title').annotate(
            coverage_count=Count('technical_title'))
        for item in coverage_titles:
            data.append(
                {
                    'title': item['technical_title'],
                    'coverage_count': item['coverage_count'],
                    'total_count': User.objects.filter(
                        technical_title=item['technical_title']).count()
                }
            )
        # merge titles which we are not interested in into single group
        # labled with other_label
        if interest_titles is not None:
            item_other = {
                'title': other_label, 'coverage_count': 0, 'total_count': 0
                }
            for item in data[:]:
                if item['title'] not in interest_titles:
                    item_other['coverage_count'] += item['coverage_count']
                    item_other['total_count'] += item['total_count']
                    data.remove(item)
            if item_other['coverage_count'] > 0:
                data.append(item_other)
        return data

    @staticmethod
    def groupby_departments(users_qs):
        '''按照部门分组

        Parameters
        -------
        users_qs: QuerySet
            待分组的User查询集

        Returns
        ------
        list of dict
            按部门后分组后的结果，list包含的元素dict定义为： {
                department: string,
                coverage_count: int,
                    参数users_qs包含的用户中，隶属该部门的用户人数。
                total_count: int
                    系统里隶属该部门的用户总人数。
            }
        '''
        data = []
        coverage_departments = users_qs.values(
            'administrative_department__name').annotate(coverage_count=Count(
                'administrative_department__name'))
        for item in coverage_departments:
            data.append(
                {
                    'department': item['administrative_department__name'],
                    'coverage_count': item['coverage_count'],
                    'total_count': User.objects.filter(
                        administrative_department__name=item[
                            'administrative_department__name']).count()
                }
            )
        return data

    @staticmethod
    def get_traning_records(user, program_id=None, department_id=None,
                            start_time=None, end_time=None):
        '''根据项目ID和起始时间查询所有的培训活动的所有的培训记录（包含校内和校外活动)

        Parameters
        ----
        user: User
            执行此操作的用户

        program_id: int
            培训项目ID，为None表示查询所有的培训项目。

        department_id: int
            需要导出培训项目所属的部门，非校级管理员必须给此参数，校级管理员为此参数None则导出所有院系的所有培训项目。

        start_time: datetime
            培训活动开始时间

        end_time: datetime
            培训活动结束时间

        Return
        ------

        QuerySet
            包含Record的查询集
        '''
        if user is None or not (user.is_department_admin or user
                                .is_school_admin):
            raise BadRequest('你不是管理员，无权操作。')

        if department_id is not None:
            department = Department.objects.filter(id=department_id)
            if not department:
                raise BadRequest('部门不存在。')
            if not (user.is_school_admin or user.check_department_admin(
                    department[0])):
                raise BadRequest('你不是该院系的管理员，无权操作。')
            department_ids = [department_id]
        else:
            if user.is_school_admin:
                departments = DepartmentService.get_top_level_departments()
                dlut = Department.objects.filter(name='大连理工大学')
                department_ids = departments.union(dlut).values_list(
                    'id', flat=True)
            else:
                raise BadRequest('你不是校级管理员，必须指定部门ID。')
        if end_time is None:
            end_time = now()
        if start_time is None:
            start_time = end_time.replace(month=1, day=1, hour=0, minute=0,
                                          second=0)

        if program_id is not None:
            off_campus_event_records = Record.objects.none()
            program = Program.objects.filter(id=program_id)
            if not program:
                raise BadRequest('培训项目不存在。')
            if program[0].department.id not in department_ids:
                raise BadRequest('该培训项目不属于你管理的院系。')
            valid_program_ids = [program_id]
        else:
            off_campus_event_records = Record.objects.filter(
                off_campus_event__time__range=(start_time, end_time),
                user__administrative_department_id__in=department_ids)
            valid_program_ids = list(
                Program.objects.filter(
                    department_id__in=department_ids).values_list(
                        'id', flat=True))
        campus_event_records = Record.objects.filter(
            campus_event__isnull=False,
            campus_event__program_id__in=valid_program_ids,
            campus_event__time__range=(start_time, end_time)
            )
        records = campus_event_records.union(off_campus_event_records)
        return records.filter(
            user__teaching_type__in=('专任教师', '实验技术人员'),
            user__administrative_department__department_type='T3')
