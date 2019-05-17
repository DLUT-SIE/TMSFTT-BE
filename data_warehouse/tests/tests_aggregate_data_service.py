'''Unit tests for aggregate data services.'''
from unittest.mock import patch, Mock

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.http import HttpRequest
from django.utils.timezone import now
from django.contrib.auth.models import Group
from model_mommy import mommy

from auth.models import Department
from data_warehouse.services.aggregate_data_service import (
    AggregateDataService, TeachersGroupService,
    RecordsGroupService
)
from infra.exceptions import BadRequest
from training_event.models import CampusEvent, OffCampusEvent
from training_record.models import Record


User = get_user_model()


class TestAggregateDataService(TestCase):
    '''Test services provided by AggregateDataService.'''
    def setUp(self):
        self.dlut_group = mommy.make(Group, name="大连理工大学-管理员")
        self.user = mommy.make(User)
        self.user.groups.add(self.dlut_group)
        self.request = HttpRequest()
        self.request.user = self.user
        self.method_name = 'abcd'
        self.context = {'request': self.request}
        self.department_dlut = mommy.make(
            Department, name='大连理工大学', id=1,
            create_time=now(), update_time=now())
        top_department = mommy.make(
            Department, name='凌水主校区',
            super_department=self.department_dlut,
            create_time=now(), update_time=now())
        self.department_art = mommy.make(
            Department, name='建筑与艺术学院', id=50,
            super_department=top_department,
            department_type='T3',
            create_time=now(), update_time=now())

    def test_dispatch_error(self):
        '''Should raise BadRequest if method_name not in map's keys.'''
        with self.assertRaisesMessage(BadRequest, '错误的参数'):
            AggregateDataService.dispatch(
                self.method_name, self.context)
        self.method_name = 'get_canvas_options'
        with self.assertRaisesMessage(BadRequest, '错误的参数'):
            AggregateDataService.dispatch(
                self.method_name, self.context)

    def test_dispatch(self):
        '''Should get a aggregated data'''
        self.method_name = 'teachers_statistics'
        self.context = {'request': self.request}
        self.context['group_by'] = '0'
        self.context['department_id'] = '1'
        AggregateDataService.dispatch(
            self.method_name, self.context)

    def test_personal_summary_missing_request(self):
        '''Should raise BadRequest.'''
        with self.assertRaisesMessage(BadRequest, '参数错误'):
            AggregateDataService.personal_summary({})

    @patch('data_warehouse.services.aggregate_data_service.UserRankingService')
    @patch(
        'data_warehouse.services.aggregate_data_service.'
        'UserCoreStatisticsService')
    def test_personal_summary(
            self, mocked_user_core_service, mocked_user_ranking_service):
        '''Should return personal summary.'''
        request = Mock()
        request.user = self.user
        context = {
            'request': request,
        }

        res = AggregateDataService.personal_summary(context)

        self.assertIsInstance(res, dict)
        self.assertEqual(
            {'programs_statistics', 'events_statistics', 'records_statistics',
             'competition_award_info', 'monthly_added_records',
             'ranking_in_department', 'ranking_in_school'},
            set(res.keys())
        )
        (
            mocked_user_core_service
            .get_programs_statistics.assert_called_with(self.user)
        )
        (
            mocked_user_core_service
            .get_events_statistics.assert_called_with(self.user)
        )
        (
            mocked_user_core_service
            .get_records_statistics.assert_called_with(self.user)
        )
        (
            mocked_user_core_service
            .get_competition_award_info.assert_called_with(self.user)
        )
        (
            mocked_user_core_service
            .get_monthly_added_records_statistics.assert_called_with(self.user)
        )
        (
            mocked_user_ranking_service
            .get_total_training_hours_ranking_in_department
            .assert_called_with(self.user)
        )
        (
            mocked_user_ranking_service
            .get_total_training_hours_ranking_in_school
            .assert_called_with(self.user)
        )

    def test_teachers_statistics(self):
        '''Should get a teachers_statistics data'''
        self.context = {'request': self.request}
        self.context['department_id'] = '0'
        with self.assertRaisesMessage(BadRequest, '错误的参数'):
            AggregateDataService.teachers_statistics(self.context)
        self.context['group_by'] = '100'
        with self.assertRaisesMessage(BadRequest, '错误的参数'):
            AggregateDataService.teachers_statistics(self.context)
        self.context['group_by'] = '0'
        self.context['start_year'] = '2016'
        self.context['end_year'] = '2019'
        data = AggregateDataService.teachers_statistics(self.context)
        self.assertEqual(len(data['label']), 1)
        self.context['group_by'] = '1'
        data = AggregateDataService.teachers_statistics(self.context)
        self.assertEqual(len(data['label']), 10)
        self.context['group_by'] = '2'
        data = AggregateDataService.teachers_statistics(self.context)
        self.assertEqual(len(data['label']), 4)
        self.context['group_by'] = '3'
        data = AggregateDataService.teachers_statistics(self.context)
        self.assertEqual(len(data['label']), 3)

    def test_records_statistics(self):
        '''Should get a records_statistics data'''
        self.context = {'request': self.request}
        self.context['department_id'] = '0'
        with self.assertRaisesMessage(BadRequest, '错误的参数'):
            AggregateDataService.records_statistics(self.context)
        self.context['group_by'] = '0'
        self.context['start_year'] = '2018'
        self.context['end_year'] = '2016'
        with self.assertRaisesMessage(BadRequest, '错误的参数'):
            AggregateDataService.records_statistics(self.context)
        self.context['group_by'] = '1000'
        self.context['start_year'] = '2015'
        self.context['end_year'] = '2016'
        with self.assertRaisesMessage(BadRequest, '错误的参数'):
            AggregateDataService.records_statistics(self.context)
        self.context['group_by'] = '0'
        self.context['start_year'] = '2016'
        self.context['end_year'] = '2019'
        data = AggregateDataService.records_statistics(self.context)
        self.assertEqual(len(data['label']), 1)
        self.context['group_by'] = '1'
        data = AggregateDataService.records_statistics(self.context)
        self.assertEqual(len(data['label']), 10)
        self.context['group_by'] = '2'
        data = AggregateDataService.records_statistics(self.context)
        self.assertEqual(len(data['label']), 4)

    def test_get_users_by_department(self):
        '''Should get users queryset by department_id'''
        user = mommy.make(User)
        group2 = mommy.make(Group, name="建筑与艺术学院-管理员")

        user.groups.add(self.dlut_group)
        users = AggregateDataService.get_users_by_department(user, 1)
        self.assertTrue(users)
        users = AggregateDataService.get_users_by_department(user, 50)
        self.assertFalse(users)
        users = AggregateDataService.get_users_by_department(user, 1000)
        self.assertFalse(users)

        user.groups.remove(self.dlut_group)
        users = AggregateDataService.get_users_by_department(user, 50)
        self.assertFalse(users)
        user = mommy.make(User, administrative_department=self.department_art)
        user.groups.add(group2)
        users = AggregateDataService.get_users_by_department(user, 50)
        self.assertTrue(users)

    def test_get_records_by_time_department(self):
        '''Should get records by time and department'''
        user = mommy.make(User, administrative_department=self.department_art)
        campusevent = mommy.make(CampusEvent, time=now())
        offcampusevent = mommy.make(OffCampusEvent, time=now())
        record1 = mommy.make(
            Record, campus_event=campusevent, user=user)
        record2 = mommy.make(
            Record, off_campus_event=offcampusevent, user=user)
        user1 = mommy.make(User)
        user1.groups.add(self.dlut_group)
        time = {'start': 2020, 'end': 2019}
        with self.assertRaisesMessage(BadRequest, '错误的参数'):
            AggregateDataService.get_records_by_time_department(
                user1, 1, time)
        time = {'start': 2019, 'end': 2019}
        records = AggregateDataService.get_records_by_time_department(
            user1, 1, time)
        self.assertEqual(records['campus_records'][0].id, record1.id)
        records = AggregateDataService.get_records_by_time_department(
            user1, 50, time)
        self.assertEqual(records['campus_records'][0].id, record1.id)
        self.assertEqual(records['off_campus_records'][0].id, record2.id)
        records = AggregateDataService.get_records_by_time_department(
            user1, 5000, time)
        self.assertEqual(len(records['campus_records']), 0)
        self.assertEqual(len(records['off_campus_records']), 0)
        user2 = mommy.make(User)
        group = mommy.make(Group, name="建筑与艺术学院-管理员")
        user2.groups.add(group)
        records = AggregateDataService.get_records_by_time_department(
            user2, 50, time)
        self.assertEqual(records['campus_records'][0].id, record1.id)
        self.assertEqual(records['off_campus_records'][0].id, record2.id)


class TestTeachersGroupService(TestCase):
    '''test TeachersGroupService'''
    def setUp(self):
        self.dlut_group = mommy.make(Group, name="大连理工大学-管理员")
        self.user = mommy.make(User)
        self.user.groups.add(self.dlut_group)
        self.request = HttpRequest()
        self.request.user = self.user
        self.method_name = 'abcd'
        self.context = {'request': self.request}
        self.department_dlut = mommy.make(
            Department, name='大连理工大学', id=1,
            create_time=now(), update_time=now())
        top_department = mommy.make(
            Department, name='凌水主校区',
            super_department=self.department_dlut,
            create_time=now(), update_time=now())
        self.department_art = mommy.make(
            Department, name='建筑与艺术学院', id=50,
            super_department=top_department,
            department_type='T3',
            create_time=now(), update_time=now())

    def test_group_users_by_technical_title(self):
        '''Should get a group users by technical_title'''
        user1 = mommy.make(User, technical_title='教授')
        user2 = mommy.make(User, technical_title='副教授')
        user3 = mommy.make(User, technical_title='讲师（高校）')
        users = User.objects.all()
        group_users = TeachersGroupService.group_users_by_technical_title(
            users, count_only=True
        )
        self.assertEqual(group_users['教授'], 1)
        group_users = TeachersGroupService.group_users_by_technical_title(
            users, count_only=False
        )
        self.assertEqual(
            group_users['教授'][0].id, user1.id)
        self.assertEqual(
            group_users['副教授'][0].id, user2.id)
        self.assertEqual(
            group_users['讲师（高校）'][0].id, user3.id)

    def test_group_users_by_education_background(self):
        '''Should get a group users by education_background'''
        user1 = mommy.make(User, education_background='博士研究生毕业')
        user2 = mommy.make(User, education_background='研究生毕业')
        user3 = mommy.make(User, education_background='大学本科毕业')
        users = User.objects.all()
        group_users = TeachersGroupService.group_users_by_education_background(
            users, count_only=True
        )
        self.assertEqual(group_users['博士研究生毕业'], 1)
        group_users = TeachersGroupService.group_users_by_education_background(
            users, count_only=False
        )
        self.assertEqual(
            group_users['博士研究生毕业'][0].id, user1.id)
        self.assertEqual(
            group_users['研究生毕业'][0].id, user2.id)
        self.assertEqual(
            group_users['大学本科毕业'][0].id, user3.id)

    def test_group_users_by_department(self):
        '''Should get a group users by department'''
        user1 = mommy.make(User, administrative_department=self.department_art)
        users = User.objects.all()
        group_users = TeachersGroupService.group_users_by_department(
            users, count_only=True
        )
        self.assertEqual(group_users['建筑与艺术学院'], 1)
        group_users = TeachersGroupService.group_users_by_department(
            users, count_only=False
        )
        self.assertEqual(
            group_users['建筑与艺术学院'][0].id, user1.id)

    def test_group_users_by_age(self):
        '''Should get a group users by age'''
        user1 = mommy.make(User, age=12)
        user2 = mommy.make(User, age=45)
        users = User.objects.all()
        group_users = TeachersGroupService.group_users_by_age(
            users, count_only=True
        )
        self.assertEqual(group_users['35岁及以下'], 3)
        group_users = TeachersGroupService.group_users_by_age(
            users, count_only=False
        )
        self.assertEqual(
            group_users['35岁及以下'][2].id, user1.id)
        self.assertEqual(
            group_users['36~45岁'][0].id, user2.id)


class TestRecordsGroupService(TestCase):
    '''test RecordsGroupService'''
    def setUp(self):
        self.dlut_group = mommy.make(Group, name="大连理工大学-管理员")
        self.user = mommy.make(User)
        self.user.groups.add(self.dlut_group)
        self.request = HttpRequest()
        self.request.user = self.user
        self.method_name = 'abcd'
        self.context = {'request': self.request}
        self.department_dlut = mommy.make(
            Department, name='大连理工大学', id=1,
            create_time=now(), update_time=now())
        top_department = mommy.make(
            Department, name='凌水主校区',
            super_department=self.department_dlut,
            create_time=now(), update_time=now())
        self.department_art = mommy.make(
            Department, name='建筑与艺术学院', id=50,
            super_department=top_department,
            department_type='T3',
            create_time=now(), update_time=now())

    def test_group_records_by_age(self):
        '''Should get group records by age'''
        user1 = mommy.make(User, age=12)
        user2 = mommy.make(User, age=45)
        campusevent = mommy.make(CampusEvent, time=now())
        offcampusevent = mommy.make(OffCampusEvent, time=now())
        record1 = mommy.make(
            Record, campus_event=campusevent, user=user1)
        record2 = mommy.make(
            Record, off_campus_event=offcampusevent, user=user2)
        records = Record.objects.all()
        group_records = RecordsGroupService.group_records_by_age(
            records, count_only=True)
        self.assertEqual(group_records['35岁及以下'], 1)
        group_records = RecordsGroupService.group_records_by_age(
            records, count_only=False)
        self.assertEqual(
            group_records['35岁及以下'][0].id, record1.id)
        self.assertEqual(
            group_records['36~45岁'][0].id, record2.id)

    def test_group_records_by_department(self):
        '''Should get group records by department'''
        user1 = mommy.make(
            User, administrative_department=self.department_art)
        campusevent = mommy.make(CampusEvent, time=now())
        record1 = mommy.make(
            Record, campus_event=campusevent, user=user1)
        records = Record.objects.all()
        group_records = RecordsGroupService.group_records_by_department(
            records, count_only=True)
        self.assertEqual(group_records['建筑与艺术学院'], 1)
        group_records = RecordsGroupService.group_records_by_department(
            records, count_only=False)
        self.assertEqual(
            group_records['建筑与艺术学院'][0].id, record1.id)

    def test_group_records_by_technical_title(self):
        '''Should get group records by technical_title'''
        user1 = mommy.make(
            User, technical_title='教授')
        user2 = mommy.make(
            User, technical_title='副教授')
        campusevent = mommy.make(CampusEvent, time=now())
        offcampusevent = mommy.make(OffCampusEvent, time=now())
        record1 = mommy.make(
            Record, campus_event=campusevent, user=user1)
        record2 = mommy.make(
            Record, off_campus_event=offcampusevent, user=user2)
        records = Record.objects.all()
        group_records = RecordsGroupService.group_records_by_technical_title(
            records, count_only=True)
        self.assertEqual(group_records['教授'], 1)
        group_records = RecordsGroupService.group_records_by_technical_title(
            records, count_only=False)
        self.assertEqual(
            group_records['副教授'][0].id, record2.id)
        self.assertEqual(
            group_records['教授'][0].id, record1.id)
