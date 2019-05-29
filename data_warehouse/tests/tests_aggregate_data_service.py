'''Unit tests for aggregate data services.'''
from unittest.mock import patch, Mock, PropertyMock, MagicMock

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.http import HttpRequest
from django.utils.timezone import now
from django.contrib.auth.models import Group
from model_mommy import mommy

from auth.models import Department
from data_warehouse.services import (
    AggregateDataService
)
from infra.exceptions import BadRequest


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
            .get_programs_statistics.assert_called()
        )
        (
            mocked_user_core_service
            .get_events_statistics.assert_called()
        )
        (
            mocked_user_core_service
            .get_records_statistics.assert_called()
        )
        (
            mocked_user_core_service
            .get_competition_award_info.assert_called()
        )
        (
            mocked_user_core_service
            .get_monthly_added_records_statistics.assert_called()
        )
        (
            mocked_user_ranking_service
            .get_total_training_hours_ranking_in_department
            .assert_called()
        )
        (
            mocked_user_ranking_service
            .get_total_training_hours_ranking_in_school
            .assert_called()
        )

    @patch(
        'data_warehouse.services.aggregate_data_service.'
        'SchoolCoreStatisticsService')
    def test_school_summary(self, mocked_school_core_service):
        '''Should return school summary.'''
        res = AggregateDataService.school_summary({})

        self.assertIsInstance(res, dict)
        self.assertEqual(
            {'events_statistics', 'records_statistics',
             'department_records_statistics',
             'monthly_added_records_statistics'},
            set(res.keys())
        )
        (
            mocked_school_core_service
            .get_events_statistics.assert_called()
        )
        (
            mocked_school_core_service
            .get_records_statistics.assert_called()
        )
        (
            mocked_school_core_service
            .get_department_records_statistics()
        )
        (
            mocked_school_core_service
            .get_monthly_added_records_statistics()
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
        self.assertEqual(len(data['label']), 11)
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
        self.assertEqual(len(data['label']), 11)
        self.context['group_by'] = '2'
        data = AggregateDataService.records_statistics(self.context)
        self.assertEqual(len(data['label']), 4)

    @patch('data_warehouse.services.aggregate_data_service'
           '.CoverageStatisticsService')
    @patch('data_warehouse.services.aggregate_data_service.TableExportService')
    def test_table_coverage_statistics(
            self, mock_table_export_service, mock_coverage_statistics_service):
        '''Should 根据请求返回分组后的培训记录'''
        request = Mock()
        context = {
            'request': None,
        }
        context['request'] = request
        context['start_time'] = now()
        context['end_time'] = now()
        AggregateDataService.table_coverage_statistics(context)
        (
            mock_coverage_statistics_service
            .get_training_records.assert_called_with(
                request.user,
                None,
                None,
                context['start_time'],
                context['end_time']
            )
        )
        (
            mock_coverage_statistics_service
            .groupby_ages.assert_called()
        )
        (
            mock_coverage_statistics_service
            .groupby_departments.assert_called()
        )
        (
            mock_coverage_statistics_service
            .groupby_titles.assert_called()

        )
        (
            mock_table_export_service
            .export_traning_coverage_summary.assert_called()
        )

    @patch('data_warehouse.services.aggregate_data_service'
           '.AggregateDataService.table_coverage_statistics')
    def test_table_export(self, mocked_coverage_statistics):
        '''Should 应该正确的分发表格导出请求'''
        request = MagicMock()
        context = {}
        context['request'] = request
        context['table_type'] = 4
        AggregateDataService.table_export(context)
        mocked_coverage_statistics.assert_called()

    def test_coverage_statistics(self):
        '''Should get coverage statistics data'''
        self.context = {'request': self.request}
        self.context['department_id'] = '0'
        self.context['program_id'] = '0'
        self.context['start_year'] = '2019'
        self.context['end_year'] = '2019'
        with self.assertRaisesMessage(BadRequest, '错误的参数'):
            AggregateDataService.coverage_statistics(self.context)
        self.context['group_by'] = '100'
        with self.assertRaisesMessage(BadRequest, '错误的参数'):
            AggregateDataService.coverage_statistics(self.context)
        self.context['group_by'] = '2'
        data = AggregateDataService.coverage_statistics(self.context)
        self.assertEqual(len(data['label']), 4)
        self.context['department_id'] = '50'
        data = AggregateDataService.coverage_statistics(self.context)
        self.assertEqual(len(data['label']), 4)

    @patch('data_warehouse.services.aggregate_data_service'
           '.CampusEventFeedbackService')
    @patch('data_warehouse.services.aggregate_data_service'
           '.TableExportService')
    def test_table_training_feedback(self, mock_table_export_service,
                                     mock_campus_event_feedback_service):
        '''Should 正确的处理培训反馈'''
        context = {}
        with self.assertRaisesMessage(ValueError, '未在context参数中指定request，'
                                      '或context类型不为dict。'):
            AggregateDataService.table_training_feedback(context)
        request = MagicMock()
        request.user = MagicMock()
        type(request.user).is_department_admin = PropertyMock(
            return_value=False)
        type(request.user).is_school_admin = PropertyMock(return_value=False)
        context = {'request': request}
        with self.assertRaisesMessage(BadRequest, '你不是管理员。'):
            AggregateDataService.table_training_feedback(context)
        request = Mock()
        context = {
            'request': request,
            'program_id': 1,
            }
        AggregateDataService.table_training_feedback(context)
        mock_campus_event_feedback_service.get_feedbacks.assert_called_with(
            request.user,
            [1]
        )
        mock_table_export_service.export_training_feedback.assert_called()

    @patch('data_warehouse.services.aggregate_data_service'
           '.TrainingHoursStatisticsService')
    @patch('data_warehouse.services.aggregate_data_service'
           '.TableExportService')
    def test_table_training_hours(self, mock_table_export_service,
                                  mock_training_hours_service):
        '''Should 正确的处理培训学时统计'''
        context = {}
        with self.assertRaisesMessage(ValueError, '未在context参数中指定request，'
                                      '或context类型不为dict。'):
            AggregateDataService.table_training_hours_statistics(context)
        request = MagicMock()
        request.user = MagicMock()
        type(request.user).is_department_admin = PropertyMock(
            return_value=False)
        type(request.user).is_school_admin = PropertyMock(return_value=False)
        context = {'request': request}
        with self.assertRaisesMessage(BadRequest, '你不是管理员。'):
            AggregateDataService.table_training_hours_statistics(context)
        request = Mock()
        mock_start_time, mock_end_time = now(), now()
        context = {
            'request': request,
            'start_time': mock_start_time,
            'end_time': mock_end_time
            }
        AggregateDataService.table_training_hours_statistics(context)
        mock_training_hours_service.get_training_hours_data.assert_called_with(
            request.user,
            mock_start_time,
            mock_end_time
        )
        mock_table_export_service.export_training_hours.assert_called()

    @patch('data_warehouse.services.training_record_service'
           '.TrainingRecordService')
    @patch('data_warehouse.services.aggregate_data_service'
           '.TableExportService')
    def test_table_training_records(self, mock_table_export_service,
                                    mock_training_record_service,):
        '''Should 正确的处理个人培训记录'''
        request = MagicMock()
        type(request).user = PropertyMock(return_value=self.user)
        context = {
            'request': request,
            'event_name': '1',
            'event_location': '2',
            'start_time': '2019-01-01',
            'end_time': '2019-01-01',
        }
        AggregateDataService.table_training_records(context)

        mock_training_record_service.get_records.return_value = []
        mock_table_export_service.export_records_for_user.assert_called()

    @patch('data_warehouse.services.aggregate_data_service'
           '.TrainingHoursStatisticsService')
    def test_get_group_hours_data(self, mock_training_hours_service):
        '''test get group hours data'''
        context = {}
        context['request'] = self.request
        context['start_year'] = 'qqq'
        context['end_year'] = 'www'
        with self.assertRaisesMessage(BadRequest, '错误的参数'):
            AggregateDataService.get_group_hours_data(context)
        context['start_year'] = '2016'
        context['end_year'] = '2019'
        group_data = AggregateDataService.get_group_hours_data(context)
        mock_training_hours_service.get_training_hours_data.assert_called()
        self.assertIsNotNone(group_data)

    @patch('data_warehouse.services.aggregate_data_service'
           '.TrainingHoursStatisticsService')
    def test_training_hours_statistics(self, mock_training_hours_service):
        '''test function hours statistics'''
        context = {}
        context['request'] = self.request
        context['start_year'] = '2016'
        context['end_year'] = '2019'
        data = AggregateDataService.training_hours_statistics(context)
        mock_training_hours_service.get_training_hours_data.assert_called()
        self.assertIsNotNone(data)

    @patch('data_warehouse.services.aggregate_data_service'
           '.TableExportService')
    def test_table_teacher_statistics(self, mock_table_export_service):
        '''Should 正确的导出专任教师表'''
        context = {}
        context['request'] = self.request
        context['department_id'] = '0'
        context['group_by'] = '3'
        file_path, _ = AggregateDataService.table_teacher_statistics(
            context)
        mock_table_export_service.export_teacher_statistics.assert_called()
        self.assertIsNotNone(file_path)

    @patch('data_warehouse.services.aggregate_data_service'
           '.TableExportService')
    def test_table_training_summary(self, mock_table_export_service):
        '''Should 正确的导出专任教师表'''
        context = {}
        context['request'] = self.request
        context['department_id'] = '0'
        context['group_by'] = '3'
        context['start_time'] = now()
        context['end_time'] = now()
        file_path, _ = AggregateDataService.table_training_summary(
            context)
        (
            mock_table_export_service
            .export_training_summary.assert_called()
        )
        self.assertIsNotNone(file_path)
