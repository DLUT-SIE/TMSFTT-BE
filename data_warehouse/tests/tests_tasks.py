'''Unit tests for data_warehouse celery tasks.'''
from unittest.mock import patch

from django.test import TestCase

from data_warehouse.tasks import generate_user_rankings


class TestTasks(TestCase):
    '''Test celery tests.'''
    @patch('data_warehouse.tasks.UserRankingService')
    def test_generate_user_rankings(self, mocked_service):
        '''Should call UserRankingService.generate_user_rankings().'''
        generate_user_rankings()

        mocked_service.generate_user_rankings.assert_called()
