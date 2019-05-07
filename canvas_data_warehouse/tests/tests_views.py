'''Unit tests for data-graph views.'''
from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase
from model_mommy import mommy

from infra.exceptions import BadRequest


User = get_user_model()


class CanvasDataViewSet(APITestCase):
    '''Unit tests for DataGraphView.'''
    @classmethod
    def setUpTestData(cls):
        cls.user = mommy.make(User)

    def test_get_data(self):
        '''should return 200 when successed'''
        self.client.force_authenticate(self.user)

        url = reverse('canvas-data-get-canvas-data') + '?graph_type=1&'\
            'a=2&b=2019&c=2019&d=1'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        url = reverse('canvas-data-get-canvas-data') + '?graph=1&a=2&'\
            'b=2019&c=2019&d=1'
        response = self.client.get(url)
        self.assertRaisesMessage(BadRequest, '错误的参数格式')

    def test_get_options(self):
        '''should return 200 when successed'''
        self.client.force_authenticate(self.user)
        url = reverse('canvas-data-get-canvas-options')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)