'''Unit tests for data-graph views.'''
from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase
from model_mommy import mommy

from infra.exceptions import BadRequest


User = get_user_model()


class TestDataGraphView(APITestCase):
    '''Unit tests for DataGraphView.'''
    @classmethod
    def setUpTestData(cls):
        cls.user = mommy.make(User)

    def test_get(self):
        '''should return 200 when successed'''
        self.client.force_authenticate(self.user)

        url = reverse('data-graph') + '?y_type=1&x_type=2&'\
            'search_start_year=2019&search_end_year=2019&search_region=1'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        url = reverse('data-graph') + "?y_type=1&x_type='ab'&"\
            "search_start_year=2019&search_end_year=2019&search_region=创新"
        response = self.client.get(url)
        self.assertRaisesMessage(BadRequest, '参数格式错误')


class TestDataGraphParamView(APITestCase):
    '''Unit tests for DataGraphParamView'''
    @classmethod
    def setUpTestData(cls):
        cls.user = mommy.make(User)

    def test_get(self):
        '''should return 200 when successed'''
        self.client.force_authenticate(self.user)
        url = reverse('data-graph-param')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
