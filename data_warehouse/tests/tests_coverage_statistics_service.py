'''覆盖率服务测试'''
from django.test import TestCase
from django.contrib.auth.models import Group
from django.utils.timezone import now
from model_mommy import mommy
from data_warehouse.services.coverage_statistics_service import (
    CoverageStatisticsService)
from training_record.models import Record
from training_event.models import CampusEvent, OffCampusEvent
from training_program.models import Program
from auth.models import Department, User, UserGroup
from infra.exceptions import BadRequest


# pylint: disable=R0902
class TestCoverageStatisticsService(TestCase):
    '''测试培训覆盖率统计服务'''
    def setUp(self):
        self.mock_dept_name = (
            '创新创业学院',
            '计算机学院',
            '机械学院',
            '管理学院'
            )
        self.mock_depts = []
        for raw_dept_id, dept_name in enumerate(self.mock_dept_name):
            self.mock_depts.append(
                mommy.make(
                    Department,
                    name=dept_name,
                    raw_department_id=raw_dept_id
                )
            )
        self.mock_school = mommy.make(
            Department,
            name='大连理工大学',
            raw_department_id=999
        )

        self.mock_users_info = []
        self.mock_users_info.extend([(35, '讲师', Department.objects.get(
            name='创新创业学院')), ] * 15)
        self.mock_users_info.extend([(36, '副教授', Department.objects.get(
            name='计算机学院')), ] * 15)
        self.mock_users_info.extend([(55, '教授', Department.objects.get(
            name='机械学院')), ] * 15)
        self.mock_users_info.extend([(56, '研究员', Department.objects.get(
            name='管理学院')), ] * 15)
        self.mock_users = []
        for user_info in self.mock_users_info:
            self.mock_users.append(
                mommy.make(
                    User,
                    age=user_info[0],
                    technical_title=user_info[1],
                    department=user_info[2],
                    administrative_department=user_info[2]
                )
            )
        assert len(self.mock_users) == 60

        self.mock_program_sie = mommy.make(
            Program,
            name='测试的创新创业学院培训项目',
            department=Department.objects.get(name='创新创业学院')
        )
        self.mock_program_ms = mommy.make(
            Program,
            name='测试的管院培训项目',
            department=Department.objects.get(name='管理学院')
        )

        self.campus_event_sie_program = mommy.make(
            CampusEvent,
            program=self.mock_program_sie
        )
        # mock一些2000年到2008年到培训活动
        times = [now().replace(
            year=i, month=1, day=1, hour=0, minute=0, second=0
            ) for i in range(2000, 2009)]
        assert len(times) == 9
        self.records_on_campus_event_sie_program_2000_2008 = []
        for time in times:
            self.records_on_campus_event_sie_program_2000_2008.append(
                mommy.make(
                    Record,
                    user=self.mock_users[-1],
                    campus_event__time=time,
                    campus_event__program=self.mock_program_sie,
                    campus_event__name=f'测试的{time.year}创新创业学院培训活动',
                )
            )
        assert len(self.records_on_campus_event_sie_program_2000_2008) == 9
        self.off_campus_event = mommy.make(
            OffCampusEvent,
            name='测试的校外培训活动',
            _quantity=15
        )
        # 指定给创新创业学院的老师参加校外培训活动
        self.records_on_off_campus_event = []
        event_it = iter(self.off_campus_event)
        for user in User.objects.filter(department__name='创新创业学院'):
            event = next(event_it)
            self.records_on_off_campus_event.append(
                mommy.make(
                    Record,
                    off_campus_event=event,
                    user=user
                )
            )

        # 创新创业学运举办的培训项目的培训活动对应的所有培训记录
        self.records_on_campus_event_sie_program = []
        for mock_user in self.mock_users:
            self.records_on_campus_event_sie_program.extend(
                mommy.make(
                    Record,
                    campus_event=self.campus_event_sie_program,
                    user=mock_user,
                    _quantity=10
                )
            )
        # mock校级管理员 & 创新创业学院管理员
        self.super_admin_group = mommy.make(
            Group,
            name='大连理工大学-管理员'
        )
        self.sie_admin_group = mommy.make(
            Group,
            name='创新创业学院-管理员'
        )
        self.school_admin = mommy.make(
            User,
            is_superuser=True,
            department=self.mock_school
        )
        self.sie_admin = mommy.make(
            User,
            department=Department.objects.get(name='创新创业学院')
        )
        self.mock_normal_user = mommy.make(
            User
        )
        mommy.make(
            UserGroup,
            user=self.sie_admin,
            group=self.sie_admin_group
        )
        mommy.make(
            UserGroup,
            user=self.school_admin,
            group=self.super_admin_group
        )
        assert self.school_admin.is_school_admin
        assert self.sie_admin.is_department_admin
        assert self.sie_admin.check_department_admin(Department.objects.get(
            name='创新创业学院'))

    def test_groupby_ages(self):
        '''Should 按年龄段对用户查询集分组统计'''
        user_qs = User.objects.all()
        got = CoverageStatisticsService.groupby_ages(user_qs)
        self.assertIsInstance(got, list)
        for item in got:
            self.assertEqual(
                item.keys(),
                {
                    'total_count',
                    'coverage_count',
                    'age_range'
                }
            )
            self.assertGreaterEqual(item['total_count'],
                                    item['coverage_count'])

    def test_groupby_titles(self):
        '''Should 按职称对用户查询集分组统计'''
        user_qs = User.objects.all()
        got = CoverageStatisticsService.groupby_titles(user_qs)
        self.assertIsInstance(got, list)
        for item in got:
            self.assertEqual(
                item.keys(),
                {
                    'total_count',
                    'coverage_count',
                    'title'
                }
            )
            self.assertGreaterEqual(item['total_count'],
                                    item['coverage_count'])

        got = CoverageStatisticsService.groupby_titles(
            user_qs,
            ['教授', '副教授', '讲师'],
            '其他职称'
        )
        got_titles = [item['title'] for item in got]
        self.assertEqual(4, len(got_titles))
        self.assertTrue('其他职称' in got_titles)

    def test_groupby_departments(self):
        '''Should 按部门对用户查询集分组统计'''
        user_qs = User.objects.all()
        got = CoverageStatisticsService.groupby_departments(user_qs)
        self.assertIsInstance(got, list)
        for item in got:
            self.assertEqual(
                item.keys(),
                {
                    'total_count',
                    'coverage_count',
                    'department'
                }
            )
            self.assertGreaterEqual(item['total_count'],
                                    item['coverage_count'])

    def test_get_traning_records_permission(self):
        '''Should 抛出正确的异常信息'''
        program_id = 1
        end_time = now()
        start_time = end_time.replace(month=1, day=1)
        with self.assertRaisesMessage(BadRequest, '你不是管理员，无权操作。'):
            CoverageStatisticsService.get_traning_records(
                None,
                program_id,
                None,
                start_time,
                end_time,
            )
        with self.assertRaisesMessage(BadRequest, '你不是管理员，无权操作。'):
            CoverageStatisticsService.get_traning_records(
                self.mock_normal_user,
                program_id,
                None,
                start_time,
                end_time,
            )
        assert not self.sie_admin.check_department_admin(
            Department.objects.get(name='管理学院'))
        with self.assertRaisesMessage(BadRequest, '你不是该院系的管理员，无权操作。'):
            CoverageStatisticsService.get_traning_records(
                self.sie_admin,
                program_id,
                Department.objects.get(name='管理学院').id,
                start_time,
                end_time,
            )
        with self.assertRaisesMessage(BadRequest, '培训项目不存在。'):
            CoverageStatisticsService.get_traning_records(
                self.sie_admin,
                -1,
                Department.objects.get(name='创新创业学院').id,
                start_time,
                end_time,
            )
        with self.assertRaisesMessage(BadRequest, '你不是校级管理员，必须指定部门ID。'):
            CoverageStatisticsService.get_traning_records(
                self.sie_admin,
                None,
                department_id=None,
                start_time=start_time,
                end_time=end_time,
            )
        with self.assertRaisesMessage(BadRequest, '该培训项目不属于你管理的院系。'):
            CoverageStatisticsService.get_traning_records(
                self.sie_admin,
                self.mock_program_ms.id,
                Department.objects.get(name='创新创业学院').id,
                start_time,
                end_time,
            )
        with self.assertRaisesMessage(BadRequest, '部门不存在。'):
            CoverageStatisticsService.get_traning_records(
                self.sie_admin,
                self.mock_program_ms.id,
                -1,
                start_time,
                end_time,
            )

    def test_get_traning_records(self):
        '''Should 根据项目ID和起始时间查询所有的培训记录（包含校内和校外活动)'''
        end_time = now()
        start_time = end_time.replace(month=1, day=1)
        records = CoverageStatisticsService.get_traning_records(
            self.sie_admin,
            self.mock_program_sie.id,
            Department.objects.get(name='创新创业学院').id,
            start_time,
            end_time
        )
        self.assertEqual(len(records),
                         len(self.records_on_campus_event_sie_program))
        for record in records:
            user = record.user
            self.assertIsInstance(user, User)
            self.assertIsInstance(user.department, Department)

        records = CoverageStatisticsService.get_traning_records(
            self.sie_admin,
            None,
            Department.objects.get(name='创新创业学院').id,
            start_time,
            end_time
        )
        self.assertEqual(
            len(records),
            len(self.records_on_campus_event_sie_program) +
            len(self.records_on_off_campus_event)
            )

    def test_get_traning_records_time_correctness(self):
        '''Should 根据给定的时间段，导出正确的记录。'''
        end_time = now().replace(
            year=2007, month=12, day=31, hour=23, minute=59, second=59)
        start_time = now().replace(
            year=2003, month=12, day=31, hour=23, minute=59, second=59)
        records = CoverageStatisticsService.get_traning_records(
            self.sie_admin,
            None,
            Department.objects.get(name='创新创业学院').id,
            start_time,
            end_time
        )
        self.assertEqual(len(records), 4)
