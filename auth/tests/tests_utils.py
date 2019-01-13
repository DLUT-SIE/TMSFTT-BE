'''Unit tests for auth serializers.'''
from django.contrib.auth import get_user_model
from django.test import TestCase
from model_mommy import mommy

from auth.utils import get_user_secret_key


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
