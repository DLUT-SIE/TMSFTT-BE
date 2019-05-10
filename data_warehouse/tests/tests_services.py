'''Unit tests for data_warehouse services.'''

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.http import HttpRequest
from model_mommy import mommy

from infra.exceptions import BadRequest
from data_warehouse.services import AggregateDataService

User = get_user_model()


class TestAggregateDataService(TestCase):
    '''Test services provided by AggregateDataService.'''
    def setUp(self):
        self.user = mommy.make(User)
        self.request = HttpRequest()
        self.request.user = self.user
        self.graph_type = 5
        self.graph_options = {}

    def test_dispatch_error(self):
        '''Should raise BadRequest if graph_type not in map's keys.'''
        with self.assertRaisesMessage(BadRequest, '错误的参数格式'):
            AggregateDataService.dispatch(
                self.request, self.graph_type, self.graph_options)

    def test_dispatch(self):
        '''Should get a aggregated data'''
        self.graph_type = 0
        AggregateDataService.dispatch(
            self.request, self.graph_type, self.graph_options)
