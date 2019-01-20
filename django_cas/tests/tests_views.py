'''Unit tests for django_cas views.'''
from datetime import datetime, timedelta
from unittest.mock import patch, Mock

from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase


class TestLoginView(APITestCase):
    '''Unit tests for Login view.'''
    @classmethod
    def setUpTestData(cls):
        cls.user = get_user_model().objects.create_user(
            username='test', password='test')

    def test_get_should_not_be_allowed(self):
        '''Should return 405 when accessing LoginView via GET.'''
        url = reverse('cas-login')

        response = self.client.get(url)

        self.assertEqual(response.status_code,
                         status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_post_already_authenticated(self):
        '''Should redirect when user is already authenticated.'''
        url = reverse('cas-login')
        data = {}

        self.client.force_authenticate(user=self.user)  # pylint: disable=E1101
        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_302_FOUND)

    def test_post_missing_data(self):
        '''Should redirect when user is already authenticated.'''
        url = reverse('cas-login')
        data = {'ticket': 'ticket'}

        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code,
                         status.HTTP_403_FORBIDDEN)

    @patch('django_cas.views.settings')
    @patch('django_cas.views.auth')
    def test_post_authentication_failed_no_retry(
            self, mocked_auth, mocked_settings):
        '''
        Should return 403 when authentication failed and no retry is allowed.
        '''
        url = reverse('cas-login')
        data = {'ticket': 'ticket', 'service': 'service'}
        mocked_auth.authenticate.return_value = None
        mocked_settings.CAS_RETRY_LOGIN = False

        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code,
                         status.HTTP_403_FORBIDDEN)

    @patch('django_cas.views.settings')
    @patch('django_cas.views.auth')
    def test_post_authentication_failed_retry(
            self, mocked_auth, mocked_settings):
        '''
        Should redirect when authentication failed and retry is allowed.
        '''
        url = reverse('cas-login')
        data = {'ticket': 'ticket', 'service': 'service'}
        mocked_auth.authenticate.return_value = None
        mocked_settings.CAS_RETRY_LOGIN = True

        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code,
                         status.HTTP_302_FOUND)

    @patch('django_cas.views.api_settings')
    @patch('django_cas.views.settings')
    @patch('django_cas.views.auth')
    def test_post_authentication_succeed(
            self, mocked_auth, _, mocked_api_settings):
        '''Should return JWT when authentication succeed.'''
        url = reverse('cas-login')
        data = {'ticket': 'ticket', 'service': 'service'}
        user = Mock()
        mocked_auth.authenticate.return_value = user
        mocked_api_settings.JWT_EXPIRATION_DELTA = timedelta(days=12)
        mocked_api_settings.JWT_AUTH_COOKIE = True
        mocked_api_settings.JWT_AUTH_COOKIE = 'JWT_TOKEN'
        mocked_api_settings.JWT_RESPONSE_PAYLOAD_HANDLER.return_value = {}

        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code,
                         status.HTTP_200_OK)
        self.assertIsInstance(user.last_login, datetime)
        user.save.assert_called()


class TestLogoutView(APITestCase):
    '''Unit tests for LogoutView.'''
    @patch('django_cas.views.settings')
    @patch('django_cas.views.auth')
    def test_normal_logout_with_next_page(self, _, mocked_settings):
        '''Should logout user and redirect.'''
        url = reverse('cas-logout')
        next_page = '/next-page/'
        mocked_settings.CAS_LOGOUT_COMPLETELY = False
        data = {
            'next': next_page
        }

        response = self.client.get(url, data=data)

        self.assertEqual(response.status_code, status.HTTP_302_FOUND)
        self.assertEqual(response.url, next_page)

    @patch('django_cas.views.settings')
    @patch('django_cas.views.auth')
    def test_normal_logout(self, _, mocked_settings):
        '''Should logout user and redirect.'''
        url = reverse('cas-logout')
        mocked_settings.CAS_LOGOUT_COMPLETELY = False

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_302_FOUND)
        self.assertEqual(response.url, '/')

    @patch('django_cas.views.get_logout_url')
    @patch('django_cas.views.settings')
    @patch('django_cas.views.auth')
    def test_completely_logout(self, _, mocked_settings, mocked_get_url):
        '''Should logout user and redirect.'''
        url = reverse('cas-logout')
        mocked_settings.CAS_LOGOUT_COMPLETELY = True
        mocked_get_url.return_value = '/cas-logout/'

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_302_FOUND)
        self.assertEqual(response.url, '/cas-logout/')
