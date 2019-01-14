'''Unit tests for django_cas middleware.'''
from unittest.mock import Mock

from django.conf import settings
from django.http import HttpResponseRedirect, HttpResponseForbidden
from django.contrib.auth.views import LoginView, LogoutView
from django.test import TestCase

from django_cas.middleware import CASMiddleware
from django_cas.views import (
    LoginView as CASLoginVIew,
    LogoutView as CASLogoutView,
)


class TestCASMiddleware(TestCase):
    '''Unit tests for CASMiddleware.'''
    def setUp(self):
        self.middleware = CASMiddleware()

    def test_process_view_django_login_view(self):
        '''Should redirect to cas-login when accessing django login view.'''
        request = Mock()
        view_func = Mock()
        view_func.view_class = LoginView
        middleware = self.middleware

        result = middleware.process_view(
            request, view_func, None, None)

        self.assertIsInstance(result, HttpResponseRedirect)
        self.assertIn('login', result.url)

    def test_process_view_django_logout_view(self):
        '''Should redirect to cas-logout when accessing django logout view.'''
        request = Mock()
        view_func = Mock()
        view_func.view_class = LogoutView
        middleware = self.middleware

        result = middleware.process_view(
            request, view_func, None, None)

        self.assertIsInstance(result, HttpResponseRedirect)
        self.assertIn('logout', result.url)

    def test_process_view_cas_login_view(self):
        '''Should return None when accessing CAS login view.'''
        request = Mock()
        view_func = Mock()
        view_func.view_class = CASLoginVIew
        middleware = self.middleware

        result = middleware.process_view(
            request, view_func, None, None)

        self.assertEqual(result, None)

    def test_process_view_cas_logout_view(self):
        '''Should return None when accessing CAS logout view.'''
        request = Mock()
        view_func = Mock()
        view_func.view_class = CASLogoutView
        middleware = self.middleware

        result = middleware.process_view(
            request, view_func, None, None)

        self.assertEqual(result, None)

    def test_process_view_skip_non_admin_prefix(self):
        '''Should return None when accessing non-admin view.'''
        settings.CAS_ADMIN_PREFIX = '/admin'
        request = Mock()
        request.path = '/not-admin/'
        view_func = Mock()
        middleware = self.middleware

        result = middleware.process_view(
            request, view_func, None, None)

        self.assertEqual(result, None)
        settings.CAS_ADMIN_PREFIX = None

    def test_process_view_skip_non_admin_contrib_module(self):
        '''
        Should return None when accessing views not from django.contrib.admin.
        '''
        request = Mock()
        view_func = Mock()
        view_func.__module__ = 'not-django-contrib-admin'
        middleware = self.middleware

        result = middleware.process_view(
            request, view_func, None, None)

        self.assertEqual(result, None)

    def test_process_view_skip_admin_for_console(self):
        '''Should return None when user is staff.'''
        request = Mock()
        request.user.is_authenticated = True
        request.user.is_staff = True
        view_func = Mock()
        view_func.__module__ = 'django.contrib.admin.'
        middleware = self.middleware

        result = middleware.process_view(
            request, view_func, None, None)

        self.assertEqual(result, None)

    def test_process_view_forbidden_non_admin_for_console(self):
        '''Should return 403 when user is not staff.'''
        request = Mock()
        request.user.is_authenticated = True
        request.user.is_staff = False
        view_func = Mock()
        view_func.__module__ = 'django.contrib.admin.'
        middleware = self.middleware

        result = middleware.process_view(
            request, view_func, None, None)

        self.assertIsInstance(result, HttpResponseForbidden)

    def test_process_view_redirect_not_authenticated(self):
        '''Should redirect when user is not authenticated.'''
        request = Mock()
        request.user.is_authenticated = False
        view_func = Mock()
        view_func.__module__ = 'django.contrib.admin.'
        middleware = self.middleware

        result = middleware.process_view(
            request, view_func, None, None)

        self.assertIsInstance(result, HttpResponseRedirect)
        self.assertIn('login', result.url)
