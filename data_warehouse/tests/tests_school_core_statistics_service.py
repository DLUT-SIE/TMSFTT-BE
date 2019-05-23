'''Unit tests for SchoolCoreStatisticsService.'''
from unittest.mock import patch, Mock

from django.test import TestCase
from django.utils.timezone import now
from model_mommy import mommy

from auth.models import User, Department
from training_event.models import CampusEvent
from training_record.models import Record
from data_warehouse.services.school_core_statistics_service import (
    SchoolCoreStatisticsService
)

class TestSchoolCoreStatisticsService(TestCase):
    def test_get_events_statistics(self):
        '''Should return statistics data for events.'''
        num_events = 10
        mommy.make(CampusEvent, deadline=now().replace(year=2020),
                   _quantity=num_events)
        mommy.make(CampusEvent, deadline=now().replace(year=2018),
                   _quantity=20)

        data = SchoolCoreStatisticsService.get_events_statistics()

        self.assertIsInstance(data, dict)
        self.assertEqual(data['available_to_enroll'], num_events)

    @patch('django.utils.timezone.now')
    @patch(
        'data_warehouse.services.school_core_statistics_service'
        '.UserService.get_full_time_teachers')
    def test_get_records_statistics(self, mocked_get_teachers, mocked_now):
        '''Should return statistics data for records.'''
        num_records = 100
        num_campus_records = 20
        num_reviewed_off_campus_records = 30
        num_records_added_in_current_month = (
            num_campus_records + num_reviewed_off_campus_records
        )
        mocked_now.return_value = now().replace(year=2018)
        # Off-campus records, approved, but were added in 2018
        mommy.make(
            Record,
            status=Record.STATUS_SCHOOL_ADMIN_APPROVED,
            _fill_optional=['off_campus_event'],
            _quantity=num_records - num_records_added_in_current_month)
        mocked_now.return_value = now()
        # Off-campus records, approved, were added in this month
        mommy.make(
            Record,
            status=Record.STATUS_SCHOOL_ADMIN_APPROVED,
            _fill_optional=['off_campus_event'],
            _quantity=num_reviewed_off_campus_records)
        # Campus records, were added in this month
        mommy.make(
            Record,
            _fill_optional=['campus_event'],
            _quantity=num_campus_records)
        num_users = 50
        mocked_count = Mock()
        mocked_count.count.return_value = num_users
        mocked_get_teachers.return_value = mocked_count
        num_average_records = num_records / num_users

        data = SchoolCoreStatisticsService.get_records_statistics()

        self.assertIsInstance(data, dict)
        self.assertEqual(data['num_records'], num_records)
        self.assertEqual(
            data['num_records_added_in_current_month'], 
            num_records_added_in_current_month)
        self.assertAlmostEqual(
            data['num_average_records'], num_average_records)

    @patch('django.utils.timezone.now')
    def test_get_department_records_statistics(self, mocked_now):
        '''Should return records statistics w.r.t departments.'''
        mocked_now.return_value = now().replace(year=2018)
        # Off-campus records, approved, but were added in 2018
        mommy.make(
            Record,
            status=Record.STATUS_SCHOOL_ADMIN_APPROVED,
            _fill_optional=['off_campus_event'],
            _quantity=100)
        mocked_now.return_value = now()
        department_details = [
            ('A', 100, 100),
            ('B', 70, 80),
        ]
        for department_name, num_users, num_records in department_details:
            department = mommy.make(
                Department, name=department_name, department_type='T3'
            )
            mommy.make(
                User,
                teaching_type='专任教师',
                administrative_department=department,
                _quantity=num_users,
            )
            num_campus_records = 15
            num_reviewed_off_campus_records = num_records - num_campus_records
             # Off-campus records, approved, were added in this month
            mommy.make(
                Record,
                status=Record.STATUS_SCHOOL_ADMIN_APPROVED,
                user__administrative_department=department,
                _fill_optional=['off_campus_event'],
                _quantity=num_reviewed_off_campus_records)
            # Campus records, were added in this month
            mommy.make(
                Record,
                _fill_optional=['campus_event'],
                user__administrative_department=department,
                _quantity=num_campus_records)

        res = SchoolCoreStatisticsService.get_department_records_statistics()

        self.assertIsInstance(res, dict)
        for item, expected_item in zip(res['data'], department_details):
            (expected_department_name, expected_num_users,
             expected_num_records) = expected_item
            self.assertEqual(item['department'], expected_department_name)
            self.assertEqual(item['num_users'], expected_num_users)
            self.assertEqual(item['num_records'], expected_num_records)
            
    @patch('django.utils.timezone.now')
    def test_get_monthly_added_records_statistics(self, mocked_now):
        '''Should return records statistics for latest 12 months.'''
        current_time = now()
        records = []
        months = []
        for offset in range(-12, 1):
            records.append(2 * -offset + 1)
            year = current_time.year
            month = current_time.month + offset
            if month <= 0:
                year -= 1
                month += 12
            fake_current_time = current_time.replace(
                year=year, month=month)
            mocked_now.return_value = fake_current_time
            months.append(fake_current_time.strftime('%Y年%m月'))

            mommy.make(
                Record,
                status=Record.STATUS_SCHOOL_ADMIN_APPROVED,
                _fill_optional=['off_campus_event'],
                _quantity=records[-1]
            )

        res = (
            SchoolCoreStatisticsService
            .get_monthly_added_records_statistics()
        )

        self.assertIsInstance(res, dict)
        self.assertEqual(res['months'], months)
        self.assertEqual(res['records'], records)
