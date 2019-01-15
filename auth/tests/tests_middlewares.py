'''Unit tests for auth middlewares.'''
from unittest.mock import patch, Mock
from model_mommy import mommy
from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework_jwt.settings import api_settings

from auth.middleware import JWTAuthenticationMiddleware


User = get_user_model()


# pylint: disable=W0212
class TestJWTAuthenticationMiddleware(TestCase):
    '''Unit tests for JWTAuthenticationMiddleware.'''

    def setUp(self):
        self.middleware = JWTAuthenticationMiddleware()

    def test_get_token_none(self):
        '''Should return None if no token presented.'''
        request = Mock()
        request.META = {}
        request.COOKIES = {}

        token = self.middleware._get_token(request)

        self.assertIsNone(token)

    def test_get_token_from_cookie(self):
        '''Should return token in cookie if presented.'''
        expected_token = 'cookie-token'
        request = Mock()
        request.META = {}
        request.COOKIES = {
            api_settings.JWT_AUTH_COOKIE: expected_token,
        }

        token = self.middleware._get_token(request)

        self.assertEqual(token, expected_token)

    def test_get_token_from_header(self):
        '''Should return token in header if presented.'''
        expected_token = 'header-token'
        not_expected_token = 'cookie-token'
        request = Mock()
        request.META = {
            'HTTP_AUTHORIZATION': '{} {}'.format(
                api_settings.JWT_AUTH_HEADER_PREFIX, expected_token,
            ),
        }
        request.COOKIES = {
            api_settings.JWT_AUTH_COOKIE, not_expected_token,
        }

        token = self.middleware._get_token(request)

        self.assertEqual(token, expected_token)

    @patch('auth.middleware.JWTAuthenticationMiddleware._get_token')
    def test_process_request_with_user_set(self, mocked_get_token):
        '''Should return directly if user is already set.'''
        request = Mock()
        request.user.is_anonymous = False

        self.middleware.process_request(request)

        mocked_get_token.assert_not_called()

    @patch('auth.middleware.api_settings.JWT_DECODE_HANDLER')
    @patch('auth.middleware.JWTAuthenticationMiddleware._get_token')
    def test_process_request_decode_failed(self, mocked_get_token,
                                           mocked_decode_handler):
        '''Should set anonymous user if decode failed.'''
        mocked_get_token.return_value = None
        mocked_decode_handler.side_effect = Exception()
        request = Mock(spec=[])

        self.middleware.process_request(request)

        self.assertTrue(request.user.is_anonymous)

    @patch('auth.middleware.api_settings.JWT_DECODE_HANDLER')
    @patch('auth.middleware.JWTAuthenticationMiddleware._get_token')
    def test_process_request_decode_succeed(self, mocked_get_token,
                                            mocked_decode_handler):
        '''Should set user if decode succeed.'''
        user = mommy.make(User)
        mocked_get_token.return_value = None
        mocked_decode_handler.return_value = {
            'user_id': str(user.pk),
        }
        request = Mock(spec=[])

        self.middleware.process_request(request)

        self.assertIsInstance(request.user, User)
        self.assertEqual(request.user.pk, user.pk)

    def test_get_user_with_jwt_cached_user_set(self):
        '''Should return request._jwt_cached_user if set.'''
        request = Mock()
        user = 'user'
        request._jwt_cached_user = user
        payload = Mock()

        result = self.middleware._get_user(request, payload)

        payload.get.assert_not_called()
        self.assertEqual(result, user)

    def test_get_user_no_user_id(self):
        '''Should return Anonymous user if no user_id presented.'''
        request = Mock([])
        payload = {}

        result = self.middleware._get_user(request, payload)

        self.assertTrue(result.is_anonymous)  # pylint: disable=E1101

    def test_get_user(self):
        '''Should return user if user_id presented.'''
        user = mommy.make(User)
        request = Mock([])
        payload = {
            'user_id': user.pk,
        }

        result = self.middleware._get_user(request, payload)

        self.assertIsInstance(result, User)
        self.assertEqual(result.pk, user.pk)  # pylint: disable=E1101
