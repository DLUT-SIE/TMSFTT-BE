'''培训覆盖率服务'''
from django.utils.timezone import now
from django.db.models import Q
from django.core.exceptions import ObjectDoesNotExist
from training_record.models import Record
from training_program.models import Program
from auth.models import User, Department
from infra.exceptions import BadRequest


class CoverageStatisticsService:
    '''培训覆盖率统计服务'''
    TITLES = (
        '教授', '副教授', '讲师', '助教', '教授级工程师',
        '高级工程师', '工程师', '研究员', '副研究员', '助理研究员')
    AGES = (
        ('35岁及以下', [0, 35]), ('36-45岁', [36, 45]),
        ('46-55岁', [46, 55]), ('56岁及以上', [56, 150]))

    @staticmethod
    def teacher_coverage():
        '''专任教师培训覆盖率统计'''

    # pylint: disable=R0914
    @staticmethod
    def groupby_training_records(records):
        '''对培训记录按照字段进行分组统计

        Parameters
        ------
        records: queryset
            将要被分组的培训记录

        Return
        ------
        data: dict {
            titles => dict {
                title: string
                count: int

            }
                按职称分组统计
            ages => dict {
                ages_range: string
                dict {
                    coverage_count: int,
                    total_count: int
                }
            }
                按年龄段统计
            departments => dict {
                department: string
                count: int
            }
                按学院统计
            total => int
                覆盖的总人数（不是人次，是人数）
        }
        '''
        data = {'titles': {}, 'ages': {}, 'departments': {}, 'total': -1}
        user_ids = records.values_list('user', flat=True).distinct()
        total_users_covered = len(user_ids)
        ages_groupby, titles_groupby, department_groupby = {}, {}, {}
        for uid in user_ids:
            user = User.objects.get(pk=uid)
            age = user.age
            title = user.technical_title
            department = str(user.department)
            if department in department_groupby:
                department_groupby[department]['coverage_count'] += 1
            else:
                department_groupby[department] = {}
                department_groupby[department]['coverage_count'] = 1
                department_groupby[department]['total_count'] = len(
                    User.objects.filter(department=user.department))
            if title in titles_groupby:
                titles_groupby[title]['coverage_count'] += 1
            else:
                titles_groupby[title] = {}
                titles_groupby[title]['coverage_count'] = 1
                titles_groupby[title]['total_count'] = len(User.objects.filter(
                    technical_title=title))
            low, high, mid = 0, len(CoverageStatisticsService.AGES) - 1, -1
            while low <= high:
                mid = (low + high) // 2
                small = CoverageStatisticsService.AGES[mid][1][0]
                big = CoverageStatisticsService.AGES[mid][1][1]
                if small <= age <= big:
                    break
                elif age < small:
                    high = mid - 1
                else:
                    low = mid + 1
            age_range_label = CoverageStatisticsService.AGES[mid][0]
            age_range = tuple(CoverageStatisticsService.AGES[mid][1])
            if age_range_label in ages_groupby:
                ages_groupby[age_range_label]['coverage_count'] += 1
            else:
                ages_groupby[age_range_label] = {}
                ages_groupby[age_range_label]['coverage_count'] = 1
                ages_groupby[age_range_label]['total_count'] = len(
                    User.objects.filter(age__range=age_range))
        data['titles'] = titles_groupby
        data['ages'] = ages_groupby
        data['departments'] = department_groupby
        data['total'] = total_users_covered
        return data

    # pylint: disable=R0912
    @staticmethod
    def get_traning_records(user, program_id, department_id=None,
                            start_time=None, end_time=None):
        '''根据项目ID和起始时间查询所有的培训活动的所有的培训记录（包含校内和校外活动)

        Parameters
        ----
        user: User
            执行此操作的用户

        program_ids: int
            培训项目ID，为None或者-999表示查询所有的培训项目。

        department_id: int
            需要导出培训项目所属的部门，为None则导出当前用户有权管理的院系的所有培训项目。

        start_time: datetime
            培训活动开始时间

        end_time: datetime
            培训活动结束时间

        Return
        ------

        record: queryset
            包含Record的查询集
        '''
        department_ids = []
        if user is None or not (user.is_department_admin or user
                                .is_school_admin):
            raise BadRequest('你不是管理员，无权操作。')
        else:
            if department_id is not None:
                try:
                    department = Department.objects.get(id=department_id)
                except ObjectDoesNotExist:
                    department = None
                if department is None:
                    raise BadRequest('部门不存在。')
                if not user.check_department_admin(department):
                    raise BadRequest('你不是该院系的管理员，无权操作。')
                department_ids.append(department_id)
            else:
                if user.is_school_admin:
                    department_ids.extend([
                        dept.id for dept in Department.objects.all()])
                else:
                    department_ids.append(user.department.id)
        assert department_ids
        if start_time is None or end_time is None:
            end_time = now()
            start_time = end_time.replace(month=1, day=1, hour=0, minute=0,
                                          second=0)
        if program_id not in [-999, '-999']:
            try:
                program = Program.objects.get(id=program_id)
            except ObjectDoesNotExist:
                program = None
            if program is None:
                raise BadRequest('培训项目不存在。')
            if program.department.id not in department_ids:
                raise BadRequest('该培训项目不属于你管理的院系。')
            records = Record.objects.filter(
                campus_event__isnull=False,
                campus_event__program_id=program_id,
                campus_event__time__range=(start_time, end_time)
                ).select_related('user').select_related('user__department')
        else:
            # 查询所有的培训项目对应的培训活动，包含校外活动
            valid_programs = Program.objects.filter(
                department__in=department_ids)
            departments = Department.objects.filter(id__in=department_ids)
            records = Record.objects.filter(
                (
                    Q(campus_event__time__range=(start_time, end_time)) &
                    Q(campus_event__program__in=valid_programs)
                )
                |
                (
                    Q(off_campus_event__time__range=(start_time, end_time)) &
                    Q(user__administrative_department__in=departments)
                )
            ).select_related('user').select_related('user__department')
        return records
