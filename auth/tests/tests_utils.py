'''Unit tests for auth serializers.'''
from unittest.mock import Mock

from django.contrib.auth import get_user_model
from django.test import TestCase
from model_mommy import mommy

from auth.utils import get_user_secret_key, jwt_response_payload_handler


class TestGetUserSecretKey(TestCase):
    '''Unit tests for get_user_secret_key().'''
    def test_consistent_results_for_same_user(self):
        '''Should return consistent results for same user.'''
        user = mommy.make(get_user_model())

        user_secret_key = get_user_secret_key(user)
        user_secret_key2 = get_user_secret_key(user)

        self.assertEqual(user_secret_key, user_secret_key2)

    def test_different_results_for_different_user(self):
        '''Should return different results for different user.'''
        user1 = mommy.make(get_user_model())
        user2 = mommy.make(get_user_model())

        user_secret_key1 = get_user_secret_key(user1)
        user_secret_key2 = get_user_secret_key(user2)

        self.assertNotEqual(user_secret_key1, user_secret_key2)


class TestJWTResponsePayloadHandler(TestCase):
    '''Unit tests for jwt_response_payload_handler().'''
    def test_should_include_keys(self):
        user = mommy.make(get_user_model())
        request = Mock()
        expected_keys = {'user', 'token'}

        keys = set(jwt_response_payload_handler('', user, request).keys())

        self.assertEqual(keys, expected_keys)
