'''Unit tests for django_cas utils.'''
import copy
from urllib.parse import urlencode, urljoin
from unittest.mock import patch, Mock

from django.conf import settings as default_settings
from django.test import TestCase


from django_cas.utils import (
    get_redirect_url,
    get_login_url,
    get_logout_url,
    logout,
)


class TestGetRedirectURL(TestCase):
    '''Unit tests for get_redirect_url().'''
    def setUp(self):
        self.settings = copy.deepcopy(default_settings)

    def test_redirect_page_user_specified(self):
        '''Should redirect to page user specified.'''
        next_page = '/next-page'
        request = Mock()
        request.GET.get.return_value = next_page

        result = get_redirect_url(request)

        self.assertEqual(result, next_page)

    def test_redirect_to_cas_redirect_url(self):
        '''
        Should redirect to CAS_REDIRECT_URL if CAS_IGNORE_REFERER is True.
        '''
        next_page = '/cas-next'
        request = Mock()
        request.GET.get.return_value = None
        request.is_secure.return_value = False
        request.get_host.return_value = 'localhost:8000'
        settings = self.settings
        settings.CAS_IGNORE_REFERER = True
        settings.CAS_REDIRECT_URL = next_page

        with patch('django_cas.utils.settings', settings):
            result = get_redirect_url(request)

        self.assertEqual(result, next_page)

    def test_redirect_to_referer(self):
        '''Should redirect to referer if CAS_IGNORE_REFERER is False.'''
        next_page = '/referer'
        full_next_page = 'http://localhost:8000/referer'
        request = Mock()
        request.GET.get.return_value = None
        request.META.get.return_value = full_next_page
        request.is_secure.return_value = False
        request.get_host.return_value = 'localhost:8000'
        settings = self.settings
        settings.CAS_IGNORE_REFERER = False

        with patch('django_cas.utils.settings', settings):
            result = get_redirect_url(request)

        self.assertEqual(result, next_page)


class TestGetLoginUrl(TestCase):
    '''Unit tests for get_login_url().'''
    def setUp(self):
        self.settings = copy.deepcopy(default_settings)
        self.settings.CAS_SERVER_URL = 'http://server/'

    def test_get_login_url(self):
        '''Should return CAS login URL.'''
        service = '/service'
        settings = self.settings
        settings.CAS_EXTRA_LOGIN_PARAMS = False
        params = {
            'service': service,
        }
        expected_login_url = 'http://server/login?' + urlencode(params)

        with patch('django_cas.utils.settings', settings):
            result = get_login_url(service)

        self.assertEqual(result, expected_login_url)

    def test_get_login_url_extra_params(self):
        '''Should return CAS login URL with extra params.'''
        service = '/service'
        settings = self.settings
        extra_params = {'param': 'a'}
        settings.CAS_EXTRA_LOGIN_PARAMS = extra_params
        expected_login_url = 'http://server/login'

        with patch('django_cas.utils.settings', settings):
            result = get_login_url(service)

        self.assertIn(expected_login_url, result)
        self.assertIn(urlencode({'service': service}), result)
        self.assertIn(urlencode(extra_params), result)


class TestGetLogoutUrl(TestCase):
    '''Unit tests for get_logout_url().'''
    def setUp(self):
        self.settings = copy.deepcopy(default_settings)
        self.settings.CAS_SERVER_URL = 'http://server/'

    def test_get_logout_url(self):
        '''Should return CAS logout URL.'''
        request = Mock()
        settings = self.settings
        expected_url = urljoin(self.settings.CAS_SERVER_URL, 'logout')

        with patch('django_cas.utils.settings', settings):
            result = get_logout_url(request)

        self.assertEqual(result, expected_url)

    def test_get_logout_url_with_next_page(self):
        '''Should return CAS logout URL.'''
        next_page = '/next-page'
        request = Mock()
        request.is_secure.return_value = False
        request.get_host.return_value = 'host'
        settings = self.settings
        expected_url = urljoin(self.settings.CAS_SERVER_URL, 'logout')
        expected_url += '?' + urlencode({'url': 'http://host/next-page'})

        with patch('django_cas.utils.settings', settings):
            result = get_logout_url(request, next_page=next_page)

        self.assertEqual(result, expected_url)


class TestLogout(TestCase):
    '''Unit tests for logout().'''
    def test_logout_unauthenticated_user(self):  # pylint: disable=R0201
        '''Should do nothing.'''
        request = Mock()
        request.user.is_authenticated = False

        logout(request)

        request.user.save.assert_not_called()

    def test_logout_authenticated_user(self):  # pylint: disable=R0201
        '''Should do nothing.'''
        request = Mock()
        request.user.is_authenticated = True

        logout(request)

        request.user.set_unusable_password.assert_called()
        request.user.save.assert_called()
