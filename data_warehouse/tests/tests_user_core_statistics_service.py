'''Unit tests for user core statistics services.'''
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.utils.timezone import now
from model_mommy import mommy

from data_warehouse.services.user_core_statistics_service import (
    UserCoreStatisticsService
)
from training_event.models import Enrollment, EventCoefficient
from training_record.models import Record


User = get_user_model()


class TestUserCoreStatisticsService(TestCase):
    '''Test service for providing core statistics.'''
    def setUp(self):
        self.user = mommy.make(User)

    def test_get_competition_award_info(self):
        '''Should return award info.'''
        competition = '讲课竞赛'
        level = '国家级'
        award = '一等奖'
        award_info = '|'.join([competition, level, award])
        mommy.make(
            Record,
            user=self.user,
            campus_event__name=award_info
        )
        context = {
            'start_time': now().replace(year=1970),
            'end_time': now(),
        }

        res = UserCoreStatisticsService.get_competition_award_info(
            self.user, context)

        self.assertIsInstance(res, dict)
        self.assertEqual({'timestamp', 'data', 'start_time', 'end_time'},
                         set(res.keys()))
        self.assertDictEqual(res['data'], {
            'competition': competition,
            'level': level,
            'award': award
        })

    def test_get_competition_award_info_none(self):
        '''Should return None if there is no award info.'''
        context = {
            'start_time': now(),
            'end_time': now(),
        }
        res = UserCoreStatisticsService.get_competition_award_info(
            self.user, context)

        self.assertIsInstance(res, dict)
        self.assertEqual({'timestamp', 'data', 'start_time', 'end_time'},
                         set(res.keys()))
        self.assertIsNone(res['data'])

    def test_get_monthly_added_records_statistics(self):
        '''Should return number of records added by month.'''
        current = now().replace(month=1, day=1)

        def get_year_month(idx):
            year = current.year
            if idx >= 12:
                year += 1
            month = idx % 12 + 1
            return {
                'year': year,
                'month': month,
            }

        expected_months = [
            current.replace(**get_year_month(idx)).strftime('%Y年%m月')
            for idx in range(6, 18)
        ]
        expected_campus_data = [1 + x // 3 for x in range(6, 18)]
        expected_off_campus_data = [1 + x // 2 for x in range(6, 18)]

        for idx in range(18):
            kwargs = get_year_month(idx)
            with patch('django.utils.timezone.now') as mocked_now:
                mocked_now.return_value = current.replace(**kwargs)
                mommy.make(
                    Record,
                    user=self.user,
                    _fill_optional=['campus_event'],
                    _quantity=idx // 3 + 1,
                    )
                mommy.make(
                    Record,
                    user=self.user,
                    _fill_optional=['off_campus_event'],
                    _quantity=idx // 2 + 1,
                    )

        res = UserCoreStatisticsService.get_monthly_added_records_statistics(
            self.user
        )

        self.assertIsInstance(res, dict)
        self.assertEqual(
            {'timestamp', 'months', 'campus_data', 'off_campus_data'},
            set(res.keys())
        )
        self.assertEqual(res['months'], expected_months)
        self.assertEqual(res['campus_data'], expected_campus_data)
        self.assertEqual(res['off_campus_data'], expected_off_campus_data)

    def test_get_records_statistics(self):
        '''should get data.'''
        expected_num_campus_records = 5
        expected_num_off_campus_records = 7
        total = expected_num_campus_records + expected_num_off_campus_records
        expected_campus_records_ratio = (
            expected_num_campus_records / total if total else 0
        )
        expected_off_campus_records_ratio = (
            1 - expected_campus_records_ratio if total else 0
        )
        expected_campus_records_ratio = f'{expected_campus_records_ratio:.0%}'
        expected_off_campus_records_ratio = (
            f'{expected_off_campus_records_ratio:.0%}'
        )
        mommy.make(
            Record,
            user=self.user,
            _fill_optional=['campus_event'],
            _quantity=expected_num_campus_records
        )
        mommy.make(
            Record,
            user=self.user,
            _fill_optional=['off_campus_event'],
            _quantity=expected_num_off_campus_records
        )
        context = {
            'start_time': now().replace(year=1970),
            'end_time': now(),
        }

        res = UserCoreStatisticsService.get_records_statistics(
            self.user, context)

        self.assertIsInstance(res, dict)
        self.assertEqual(
            {'timestamp', 'num_campus_records', 'num_off_campus_records',
             'campus_records_ratio', 'off_campus_records_ratio',
             'start_time', 'end_time'},
            set(res.keys())
        )
        self.assertEqual(
            res['num_campus_records'], expected_num_campus_records)
        self.assertEqual(
            res['num_off_campus_records'], expected_num_off_campus_records)
        self.assertEqual(
            res['campus_records_ratio'], expected_campus_records_ratio)
        self.assertEqual(
            res['off_campus_records_ratio'], expected_off_campus_records_ratio)

    def test_get_event_statistics(self):
        '''Should get data.'''
        expected_num_enrolled_events_not_participated = 5
        expected_num_events_as_expert = 3
        expected_num_completed_events = 10 + expected_num_events_as_expert
        expected_num_enrolled_events = (
            expected_num_completed_events
            + expected_num_enrolled_events_not_participated
        )
        # Enrolled, but not participated
        mommy.make(
            Enrollment,
            user=self.user,
            _quantity=expected_num_enrolled_events_not_participated
        )
        # Participated as a teacher
        mommy.make(
            Record,
            user=self.user,
            _fill_optional=['campus_event'],
            _quantity=(
                expected_num_completed_events
                - expected_num_events_as_expert
            )
        )
        # Participated as an expert
        mommy.make(
            Record,
            user=self.user,
            event_coefficient__role=EventCoefficient.ROLE_EXPERT,
            _fill_optional=['campus_event'],
            _quantity=expected_num_events_as_expert
        )
        context = {
            'start_time': now().replace(year=1970),
            'end_time': now(),
        }

        res = UserCoreStatisticsService.get_events_statistics(
            self.user, context)

        self.assertIsInstance(res, dict)
        self.assertEqual(
            {'timestamp', 'num_enrolled_events', 'num_completed_events',
             'num_events_as_expert', 'start_time', 'end_time'},
            set(res.keys())
        )
        self.assertEqual(
            res['num_enrolled_events'], expected_num_enrolled_events)
        self.assertEqual(
            res['num_completed_events'], expected_num_completed_events)
        self.assertEqual(
            res['num_events_as_expert'], expected_num_events_as_expert)

    def test_get_programs_statistics(self):
        '''Should get data.'''
        expected_program_names = ['A', 'B', 'C', 'D', 'E']
        expected_program_counts = [5, 11, 18, 4, 6]
        expected_data = []
        for name, count in zip(expected_program_names,
                               expected_program_counts):
            mommy.make(
                Record,
                user=self.user,
                campus_event__program__name=name,
                _quantity=count,
            )
            expected_data.append({'name': name, 'value': count})
        context = {
            'start_time': now().replace(year=1970),
            'end_time': now(),
        }
        res = UserCoreStatisticsService.get_programs_statistics(
            self.user, context)

        self.assertIsInstance(res, dict)
        self.assertEqual(
            {'timestamp', 'data', 'programs', 'start_time', 'end_time'},
            set(res.keys())
        )
        self.assertEqual(
            sorted(res['programs']), expected_program_names)
        self.assertListEqual(
            sorted(res['data'], key=lambda x: x['name']), expected_data)
