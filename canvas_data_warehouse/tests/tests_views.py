'''Unit tests for data-graph views.'''
from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase
from model_mommy import mommy


User = get_user_model()


class CanvasDataViewSet(APITestCase):
    '''Unit tests for DataGraphView.'''
    @classmethod
    def setUpTestData(cls):
        cls.user = mommy.make(User)

    def test_get(self):
        '''should return 200 when successed'''
        self.client.force_authenticate(self.user)

        url = reverse('data-graph-get-canvas-data') + '?y_type=1&x_type=2&'\
            'search_start_year=2019&search_end_year=2019&search_region=1'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_params(self):
        '''should return 200 when successed'''
        self.client.force_authenticate(self.user)
        url = reverse('data-graph-get-params')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
