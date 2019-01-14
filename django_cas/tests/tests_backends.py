'''Unit tests for django_cas backends.'''
from unittest.mock import patch, Mock

from django.contrib.auth.models import User
from django.test import TestCase

from django_cas.backends import CASBackend


class TestCASBackend(TestCase):
    '''Unit tests for CASBackend.'''
    def setUp(self):
        self.backend = CASBackend()

    @patch('django.contrib.auth.models.User.objects')
    @patch('django_cas.backends.CAS_VERIFY')
    def test_authenticate_success_return_user(self, mocked_verify,
                                              mocked_queryset):
        '''Should return existing user when authentication succeed.'''
        mocked_verify.return_value = ('username', None)
        user = Mock()
        mocked_queryset.get.return_value = user
        backend = self.backend

        result = backend.authenticate(None, None, None)

        self.assertEqual(result, user)

    @patch('django.contrib.auth.models.User.objects')
    @patch('django_cas.backends.CAS_VERIFY')
    def test_authenticate_success_create_user(self, mocked_verify,
                                              mocked_queryset):
        '''Should create user if not exsting when authentication succeed.'''
        mocked_verify.return_value = ('username', None)
        user = Mock()
        mocked_queryset.get.side_effect = User.DoesNotExist()
        mocked_queryset.create_user.return_value = user
        backend = self.backend

        result = backend.authenticate(None, None, None)

        self.assertEqual(result, user)

    @patch('django.contrib.auth.models.User.objects')
    @patch('django_cas.backends.CAS_VERIFY')
    def test_authenticate_failed_return_none(self, mocked_verify, _):
        '''Should return None when authentication failed.'''
        mocked_verify.return_value = (None, None)
        backend = self.backend

        result = backend.authenticate(None, None, None)

        self.assertEqual(result, None)
