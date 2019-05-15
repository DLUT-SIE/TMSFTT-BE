'''Unit tests for data_warehouse services.'''
from unittest.mock import patch, Mock

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.http import HttpRequest
from django.utils.timezone import now
from django.contrib.auth.models import Group
from model_mommy import mommy

from auth.models import Department
from data_warehouse.models import Ranking
from data_warehouse.services import (
    AggregateDataService, UserRankingService, UserCoreStatisticsService
)
from infra.exceptions import BadRequest
from training_event.models import Enrollment, EventCoefficient
from training_event.models import CampusEvent, OffCampusEvent
from training_record.models import Record


User = get_user_model()


class TestUserRankingService(TestCase):
    '''Unit tests for UserRankingService.'''
    def setUp(self):
        self.user = mommy.make(
            User, _fill_optional=['administrative_department'])

    @patch('data_warehouse.services.UserRankingService.round_ranking_float')
    def test_private_get_ranking(self, mocked_round):
        '''Should return ranking.'''
        ranking = Ranking.objects.create(
            user=self.user,
            ranking_type=Ranking.RANKING_BY_TOTAL_TRAINING_HOURS,
            department_id=self.user.administrative_department_id,
            ranking=1,
            value=0,
        ).ranking
        num_rankings = 10
        mommy.make(
            Ranking,
            ranking_type=Ranking.RANKING_BY_TOTAL_TRAINING_HOURS,
            department_id=self.user.administrative_department_id,
            _quantity=num_rankings)
        mocked_round.return_value = 0.15

        res = (
            UserRankingService  # pylint: disable=protected-access
            ._get_ranking(
                self.user,
                self.user.administrative_department_id,
                Ranking.RANKING_BY_TOTAL_TRAINING_HOURS,
            )
        )

        self.assertEqual(res, '前 15%')
        mocked_round.assert_called_with(ranking / (1e-5 + 1 + num_rankings))

    def test_private_get_ranking_no_data(self):
        '''Should return no data.'''
        Ranking.objects.create(
            user=self.user,
            ranking_type=Ranking.RANKING_BY_TOTAL_TRAINING_HOURS,
            department_id=self.user.administrative_department_id,
            ranking=1,
            value=0,
        )
        num_rankings = 10
        mommy.make(
            Ranking,
            ranking_type=Ranking.RANKING_BY_TOTAL_TRAINING_HOURS,
            department_id=self.user.administrative_department_id,
            _quantity=num_rankings)

        res = (
            UserRankingService  # pylint: disable=protected-access
            ._get_ranking(
                self.user,
                self.user.administrative_department_id,
                Ranking.RANKING_BY_CAMPUS_TRAINING_HOURS,
            )
        )

        self.assertEqual(res, '暂无数据')

    @patch('data_warehouse.services.UserRankingService._get_ranking')
    def test_get_total_training_hours_ranking_in_department(self, mocked_get):
        '''Should return data dict.'''
        expected_ranking = '前 10%'
        mocked_get.return_value = expected_ranking

        data = (
            UserRankingService
            .get_total_training_hours_ranking_in_department(self.user)
        )

        self.assertIn('timestamp', data)
        self.assertIn('ranking', data)
        self.assertEqual(data['ranking'], expected_ranking)
        mocked_get.assert_called_with(
            self.user, self.user.administrative_department_id,
            Ranking.RANKING_BY_TOTAL_TRAINING_HOURS
        )

        # Test cache
        new_data = (
            UserRankingService
            .get_total_training_hours_ranking_in_department(self.user)
        )

        self.assertIn('timestamp', data)
        self.assertEqual(data['timestamp'], new_data['timestamp'])

    @patch('data_warehouse.services.UserRankingService._get_ranking')
    def test_get_total_training_hours_ranking_in_school(self, mocked_get):
        '''Should return data dict.'''
        expected_ranking = '前 10%'
        mocked_get.return_value = expected_ranking
        dlut_department_id = mommy.make(
            Department, name='大连理工大学').id

        data = (
            UserRankingService
            .get_total_training_hours_ranking_in_school(self.user)
        )

        self.assertIn('timestamp', data)
        self.assertIn('ranking', data)
        self.assertEqual(data['ranking'], expected_ranking)
        mocked_get.assert_called_with(
            self.user, dlut_department_id,
            Ranking.RANKING_BY_TOTAL_TRAINING_HOURS
        )

        # Test cache
        new_data = (
            UserRankingService
            .get_total_training_hours_ranking_in_school(self.user)
        )

        self.assertIn('timestamp', data)
        self.assertEqual(data['timestamp'], new_data['timestamp'])

    def test_round_ranking_float(self):
        '''Should round float.'''
        cases = (
            (-3, 0),
            (0.09, 0.1),
            (0.12, 0.15),
            (0.18, 0.2),
            (3, 1),
        )
        for ranking_float, expected_res in cases:
            res = UserRankingService.round_ranking_float(ranking_float)
            self.assertAlmostEqual(res, expected_res)

    def test_generate_user_rankings_by_training_hours(self):
        '''Should genereate rankings.'''
        dlut_department_id = mommy.make(Department, name='大连理工大学').id
        departments = mommy.make(Department, _quantity=2)
        num_users = 10
        users = []
        for idx in range(num_users):
            department = departments[idx % len(departments)]
            user = mommy.make(
                User,
                administrative_department_id=department.id,
            )
            users.append(user)
            mommy.make(
                Record, user=user,
                campus_event__num_hours=1, _quantity=idx + 1)
            mommy.make(
                Record, user=user,
                off_campus_event__num_hours=1, _quantity=idx + 1)

        UserRankingService.generate_user_rankings_by_training_hours()

        def get_total_training_hours_ranking(user_id, department_id):
            return Ranking.objects.get(
                user_id=user_id,
                ranking_type=Ranking.RANKING_BY_TOTAL_TRAINING_HOURS,
                department_id=department_id).ranking

        ranking = get_total_training_hours_ranking(
            users[-1].id, users[-1].administrative_department_id
        )
        self.assertEqual(ranking, 1)

        ranking = get_total_training_hours_ranking(
            users[-2], users[-2].administrative_department_id
        )
        self.assertEqual(ranking, 1)

        ranking = get_total_training_hours_ranking(
            users[-1], dlut_department_id
        )
        self.assertEqual(ranking, 1)

        ranking = get_total_training_hours_ranking(
            users[-2], dlut_department_id
        )
        self.assertEqual(ranking, 2)

    @patch('data_warehouse.services.Ranking')
    @patch(
        'data_warehouse.services'
        '.UserRankingService.generate_user_rankings_by_training_hours')
    def test_generate_user_rankings(
            self, mocked_generate_by_training_hours, mocked_ranking_cls):
        '''Should call multiple generate functions.'''
        mocked_ranking_cls.objects.all.return_value = mocked_ranking_cls

        UserRankingService.generate_user_rankings()

        mocked_ranking_cls.objects.all.assert_called()
        mocked_ranking_cls.delete.assert_called()
        mocked_generate_by_training_hours.assert_called()


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

        res = UserCoreStatisticsService.get_competition_award_info(self.user)

        self.assertIsInstance(res, dict)
        self.assertEqual({'timestamp', 'data'}, set(res.keys()))
        self.assertDictEqual(res['data'], {
            'competition': competition,
            'level': level,
            'award': award
        })

        # Test cache
        new_res = UserCoreStatisticsService.get_competition_award_info(
            self.user)

        self.assertIn('timestamp', new_res)
        self.assertEqual(new_res['timestamp'], res['timestamp'])

    def test_get_competition_award_info_none(self):
        '''Should return None if there is no award info.'''
        res = UserCoreStatisticsService.get_competition_award_info(self.user)

        self.assertIsInstance(res, dict)
        self.assertEqual({'timestamp', 'data'}, set(res.keys()))
        self.assertIsNone(res['data'])

        # Test cache
        new_res = UserCoreStatisticsService.get_competition_award_info(
            self.user)

        self.assertIn('timestamp', new_res)
        self.assertEqual(new_res['timestamp'], res['timestamp'])

    def test_get_montly_added_records_statistics(self):
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

        # Test cache
        new_res = (
            UserCoreStatisticsService
            .get_monthly_added_records_statistics(self.user)
        )

        self.assertIn('timestamp', new_res)
        self.assertEqual(new_res['timestamp'], res['timestamp'])

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

        res = UserCoreStatisticsService.get_records_statistics(self.user)

        self.assertIsInstance(res, dict)
        self.assertEqual(
            {'timestamp', 'num_campus_records', 'num_off_campus_records',
             'campus_records_ratio', 'off_campus_records_ratio'},
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

        # Test cache
        new_res = UserCoreStatisticsService.get_records_statistics(self.user)

        self.assertIn('timestamp', new_res)
        self.assertEqual(new_res['timestamp'], res['timestamp'])

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

        res = UserCoreStatisticsService.get_events_statistics(self.user)

        self.assertIsInstance(res, dict)
        self.assertEqual(
            {'timestamp', 'num_enrolled_events', 'num_completed_events',
             'num_events_as_expert'},
            set(res.keys())
        )
        self.assertEqual(
            res['num_enrolled_events'], expected_num_enrolled_events)
        self.assertEqual(
            res['num_completed_events'], expected_num_completed_events)
        self.assertEqual(
            res['num_events_as_expert'], expected_num_events_as_expert)

        # Test cache
        new_res = UserCoreStatisticsService.get_events_statistics(self.user)

        self.assertIn('timestamp', new_res)
        self.assertEqual(new_res['timestamp'], res['timestamp'])

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

        res = UserCoreStatisticsService.get_programs_statistics(self.user)

        self.assertIsInstance(res, dict)
        self.assertEqual(
            {'timestamp', 'data', 'programs'},
            set(res.keys())
        )
        self.assertEqual(
            sorted(res['programs']), expected_program_names)
        self.assertListEqual(
            sorted(res['data'], key=lambda x: x['name']), expected_data)

        # Test cache
        new_res = UserCoreStatisticsService.get_programs_statistics(self.user)

        self.assertIn('timestamp', new_res)
        self.assertEqual(new_res['timestamp'], res['timestamp'])


class TestAggregateDataService(TestCase):
    '''Test services provided by AggregateDataService.'''
    def setUp(self):
        self.user = mommy.make(User)
        self.request = HttpRequest()
        self.request.user = self.user
        self.method_name = 'abcd'
        self.context = {'request': self.request}
        self.department_art = mommy.make(
            Department, name='建筑与艺术学院', id=50)
        self.department_dlut = mommy.make(
            Department, name='大连理工大学', id=1)

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

    @patch('data_warehouse.services.UserRankingService')
    @patch('data_warehouse.services.UserCoreStatisticsService')
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
        self.context['department_id'] = '1'
        with self.assertRaisesMessage(BadRequest, '错误的参数'):
            AggregateDataService.teachers_statistics(self.context)
        self.context['group_by'] = '100'
        with self.assertRaisesMessage(BadRequest, '错误的参数'):
            AggregateDataService.teachers_statistics(self.context)
        self.context['group_by'] = '0'
        self.context['start_year'] = '2016'
        self.context['end_year'] = '2019'
        data = AggregateDataService.teachers_statistics(self.context)
        self.assertEqual(len(data['label']), 0)
        self.context['group_by'] = '1'
        data = AggregateDataService.teachers_statistics(self.context)
        self.assertEqual(len(data['label']), 0)
        self.context['group_by'] = '2'
        data = AggregateDataService.teachers_statistics(self.context)
        self.assertEqual(len(data['label']), 0)
        self.context['group_by'] = '3'
        data = AggregateDataService.teachers_statistics(self.context)
        self.assertEqual(len(data['label']), 0)

    def test_records_statistics(self):
        '''Should get a records_statistics data'''
        self.context = {'request': self.request}
        self.context['department_id'] = '1'
        with self.assertRaisesMessage(BadRequest, '错误的参数'):
            AggregateDataService.records_statistics(self.context)
        self.context['group_by'] = '0'
        self.context['start_year'] = '2018'
        self.context['end_year'] = '2016'
        with self.assertRaisesMessage(BadRequest, '错误的参数'):
            AggregateDataService.records_statistics(self.context)
        self.context['group_by'] = '0'
        self.context['start_year'] = '2016'
        self.context['end_year'] = '2019'
        data = AggregateDataService.records_statistics(self.context)
        self.assertEqual(len(data['label']), 25)
        self.context['group_by'] = '1'
        data = AggregateDataService.records_statistics(self.context)
        self.assertEqual(len(data['label']), 10)
        self.context['group_by'] = '2'
        data = AggregateDataService.records_statistics(self.context)
        self.assertEqual(len(data['label']), 4)

    def test_get_users_by_department(self):
        '''Should get users queryset by department_id'''
        user = mommy.make(User)
        group1 = mommy.make(Group, name="大连理工大学-管理员")
        group2 = mommy.make(Group, name="建筑与艺术学院-管理员")

        user.groups.add(group1)
        users = AggregateDataService.get_users_by_department(user, 1)
        self.assertTrue(users)
        users = AggregateDataService.get_users_by_department(user, 1000)
        self.assertFalse(users)

        user.groups.remove(group1)
        users = AggregateDataService.get_users_by_department(user, 50)
        self.assertFalse(users)
        user = mommy.make(User, administrative_department=self.department_art)
        user.groups.add(group2)
        users = AggregateDataService.get_users_by_department(user, 50)
        self.assertTrue(users)

    def test_group_users_by_technical_title(self):
        '''Should get a group users by technical_title'''
        user1 = mommy.make(User, technical_title='教授')
        user2 = mommy.make(User, technical_title='副教授')
        user3 = mommy.make(User, technical_title='讲师（高校）')
        users = User.objects.all()
        group_users = AggregateDataService.group_users_by_technical_title(
            users, count_only=True
        )
        self.assertEqual(group_users['教授'], 1)
        group_users = AggregateDataService.group_users_by_technical_title(
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
        group_users = AggregateDataService.group_users_by_education_background(
            users, count_only=True
        )
        self.assertEqual(group_users['博士研究生毕业'], 1)
        group_users = AggregateDataService.group_users_by_education_background(
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
        group_users = AggregateDataService.group_users_by_department(
            users, count_only=True
        )
        self.assertEqual(group_users['建筑与艺术学院'], 1)
        group_users = AggregateDataService.group_users_by_department(
            users, count_only=False
        )
        self.assertEqual(
            group_users['建筑与艺术学院'][0].id, user1.id)

    def test_group_users_by_age(self):
        '''Should get a group users by age'''
        user1 = mommy.make(User, age=12)
        user2 = mommy.make(User, age=45)
        users = User.objects.all()
        group_users = AggregateDataService.group_users_by_age(
            users, count_only=True
        )
        self.assertEqual(group_users['35岁及以下'], 3)
        group_users = AggregateDataService.group_users_by_age(
            users, count_only=False
        )
        self.assertEqual(
            group_users['35岁及以下'][2].id, user1.id)
        self.assertEqual(
            group_users['36~45岁'][0].id, user2.id)

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
        group = mommy.make(Group, name="大连理工大学-管理员")
        user1.groups.add(group)
        time = {'start': 2020, 'end': 2019}
        with self.assertRaisesMessage(BadRequest, '错误的参数'):
            AggregateDataService.get_records_by_time_department(
                user1, 1, time)
        time = {'start': 2019, 'end': 2019}
        records = AggregateDataService.get_records_by_time_department(
            user1, 1, time)
        self.assertEqual(records['campus_records'][0].id, record1.id)
        user2 = mommy.make(User)
        group = mommy.make(Group, name="建筑与艺术学院-管理员")
        user2.groups.add(group)
        records = AggregateDataService.get_records_by_time_department(
            user2, 50, time)
        self.assertEqual(records['campus_records'][0].id, record1.id)
        self.assertEqual(records['off_campus_records'][0].id, record2.id)

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
        group_records = AggregateDataService.group_records_by_age(
            records, count_only=True)
        self.assertEqual(group_records['35岁及以下'], 1)
        group_records = AggregateDataService.group_records_by_age(
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
        group_records = AggregateDataService.group_records_by_department(
            records, count_only=True)
        self.assertEqual(group_records['建筑与艺术学院'], 1)
        group_records = AggregateDataService.group_records_by_department(
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
        group_records = AggregateDataService.group_records_by_technical_title(
            records, count_only=True)
        self.assertEqual(group_records['教授'], 1)
        group_records = AggregateDataService.group_records_by_technical_title(
            records, count_only=False)
        self.assertEqual(
            group_records['副教授'][0].id, record2.id)
        self.assertEqual(
            group_records['教授'][0].id, record1.id)
