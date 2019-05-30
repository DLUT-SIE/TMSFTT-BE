'''Unit tests for user_ranking services.'''
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import TestCase
from model_mommy import mommy

from auth.models import Department
from data_warehouse.models import Ranking
from data_warehouse.services.user_ranking_service import (
    UserRankingService
)
from training_record.models import Record


User = get_user_model()


class TestUserRankingService(TestCase):
    '''Unit tests for UserRankingService.'''
    def setUp(self):
        self.user = mommy.make(
            User, _fill_optional=['administrative_department'])

    @patch(
        'data_warehouse.services.user_ranking_service.'
        'UserRankingService.round_ranking_float')
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

    @patch(
        'data_warehouse.services.user_ranking_service.'
        'UserRankingService._get_ranking')
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

    @patch(
        'data_warehouse.services.user_ranking_service'
        '.UserRankingService._get_ranking')
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

    @patch('data_warehouse.services.user_ranking_service.Ranking')
    @patch(
        'data_warehouse.services.user_ranking_service'
        '.UserRankingService.generate_user_rankings_by_training_hours')
    def test_generate_user_rankings(
            self, mocked_generate_by_training_hours, mocked_ranking_cls):
        '''Should call multiple generate functions.'''
        mocked_ranking_cls.objects.all.return_value = mocked_ranking_cls

        UserRankingService.generate_user_rankings()

        mocked_ranking_cls.objects.all.assert_called()
        mocked_ranking_cls.delete.assert_called()
        mocked_generate_by_training_hours.assert_called()
