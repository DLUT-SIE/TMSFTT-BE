'''培训学时与工作量测试模块'''
from django.test import TestCase
from django.utils.timezone import now
from unittest.mock import (MagicMock, PropertyMock, patch)
from data_warehouse.services.training_hours_statistics_service import (
    TrainingHoursStatisticsService
)
from model_mommy import mommy
from auth.models import (User, Department)
from training_record.models import Record


class TestTrainingHoursStatisticsService(TestCase):
    '''培训学时与工作量测试'''
    @patch('django.utils.timezone.now')
    def setUp(self, mock_now):
        self.mock_time = now().replace(
            year=2010, month=1, day=1, hour=12, minute=0, second=0)
        mock_now.return_value = self.mock_time
        self.mock_department = mommy.make(
            Department,
            name='大连理工大学'
        )
        self.mock_department_names = [f'测试学院{idx}' for idx in range(4)]
        self.mock_departments = []
        for name in self.mock_department_names:
            self.mock_departments.append(
                mommy.make(
                    Department,
                    department_type='T3',
                    name=name
                )
            )
        self.mock_t3_users = []
        for idx in range(50):
            self.mock_t3_users.append(
                mommy.make(
                    User,
                    administrative_department=self.mock_departments[idx % 4],
                    teaching_type=('专任教师', '实验技术')[idx % 2]))
        self.mock_records = []
        for idx in range(500):
            self.mock_records.append(mommy.make(
                Record,
                campus_event__num_hours=2,
                campus_event__program__department=self.mock_department,
                user=self.mock_t3_users[idx % 50]
            ))

    @patch('data_warehouse.services.training_hours_statistics_service'
           '.CoverageStatisticsService.get_training_records')
    def test_get_training_hours_data(self, mock_get_training_records):
        '''Should 正确的获取培训工作量数据'''
        mock_get_training_records.return_value = Record.objects.filter(
            id__in=[item.id for item in self.mock_records]
        )
        self.mock_user = MagicMock()
        type(self.mock_user).is_school_admin = PropertyMock(return_value=True)
        type(self.mock_user).is_department_admin = PropertyMock(
            return_value=False)
        start_time = now().replace(year=self.mock_time.year-1)
        end_time = now().replace(year=self.mock_time.year+1)
        data = TrainingHoursStatisticsService.get_training_hours_data(
            self.mock_user, start_time, end_time)
        mock_get_training_records.assert_called()
        self.assertNotEqual(0, len(data))
        expected_keys = {'department', 'total_hours',
                         'total_coveraged_users', 'total_users'}
        for item in data:
            self.assertEqual(expected_keys, item.keys())
            self.assertGreaterEqual(
                item['total_users'], item['total_coveraged_users'])
        # department admin test case
        mock_get_training_records.return_value = Record.objects.filter(
            id__in=[item.id for item in self.mock_records],
            user__administrative_department=self.mock_departments[0]
        )
        self.mock_user = MagicMock()
        type(self.mock_user).is_school_admin = PropertyMock(return_value=False)
        type(self.mock_user).is_department_admin = PropertyMock(
            return_value=True)
        type(self.mock_user.administrative_department).id = PropertyMock(
            return_value=self.mock_departments[0].id)
        start_time = now().replace(year=self.mock_time.year-1)
        end_time = now().replace(year=self.mock_time.year+1)
        data = TrainingHoursStatisticsService.get_training_hours_data(
            self.mock_user, start_time, end_time)
        mock_get_training_records.assert_called()
        self.assertEqual(1, len(data))
        expected_keys = {'department', 'total_hours',
                         'total_coveraged_users', 'total_users'}
        self.assertEqual(expected_keys, data[0].keys())
        self.assertGreaterEqual(
            data[0]['total_users'], data[0]['total_coveraged_users'])
        self.assertEqual(data[0]['department'], self.mock_departments[0].name)
