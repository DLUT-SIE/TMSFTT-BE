'''Unit tests for data-graph views.'''
from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase
from model_mommy import mommy

from infra.exceptions import BadRequest


User = get_user_model()


class AggregateDataViewSet(APITestCase):
    '''Unit tests for DataGraphView.'''
    @classmethod
    def setUpTestData(cls):
        cls.user = mommy.make(User)

    def test_get_data(self):
        '''should return 200 when successed'''
        self.client.force_authenticate(self.user)

        url = reverse('aggregate-data-data') + '?method_name=teachers_'\
            'statistics&group_by=0&start_year=2019&end_year=2019&'\
            'department_id=1'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        url = reverse('aggregate-data-data') + '?graph=1&a=2&'\
            'b=2019&c=2019&d=1'
        response = self.client.get(url)
        self.assertRaisesMessage(BadRequest, '错误的参数格式')

    def test_get_options(self):
        '''should return 200 when successed'''
        self.client.force_authenticate(self.user)
        url = reverse('aggregate-data-options')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_export(self):
        '''Should 正确的处理表格导出请求'''
        self.client.force_authenticate(self.user)
        url = reverse('aggregate-data-table-export') + '?table_type=4'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        url = reverse('aggregate-data-table-export') + '?table_type=xyz'
        response = self.client.get(url)
        self.assertRaisesMessage(BadRequest, '请求的参数不正确。')
