'''Unit tests for auth serializers.'''
from unittest.mock import Mock, patch

from django.contrib.auth import get_user_model
from django.test import TestCase
from model_mommy import mommy

from auth.utils import (
    get_user_secret_key, jwt_response_payload_handler,
    assign_perm, remove_perm, ChoiceConverter
)


class TestUtils(TestCase):
    '''Unit tests for utility functions.'''
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

    def test_should_include_keys(self):
        '''should include key user in response data.'''
        user = mommy.make(get_user_model())
        request = Mock()
        expected_keys = {'user', 'token'}

        keys = set(jwt_response_payload_handler('', user, request).keys())

        self.assertEqual(keys, expected_keys)

    @patch('guardian.shortcuts.assign_perm')
    def test_assign_perm(self, mocked_assign_perm):
        '''Should invoke guardian.shortcuts.assign_perm.'''
        perm_name = 'perm_name'
        user_or_group = Mock()
        obj = Mock()
        assign_perm(perm_name, user_or_group, obj)

        mocked_assign_perm.assert_called_with(perm_name, user_or_group, obj)

    @patch('guardian.shortcuts.remove_perm')
    def test_remove_perm(self, mocked_remove_perm):
        '''Should invoke guardian.shortcuts.remove_perm.'''
        perm_name = 'perm_name'
        user_or_group = Mock()
        obj = Mock()
        remove_perm(perm_name, user_or_group, obj)

        mocked_remove_perm.assert_called_with(perm_name, user_or_group, obj)


class DummyConverter(ChoiceConverter):
    '''Read test mapping.'''
    mapping_name = 'test'


class TestChoiceConverter(TestCase):
    '''Unit tests for ChoiceConverter.'''
    def setUp(self):
        self.key_to_value_field_name = '_test_key_to_value'
        self.value_to_key_field_name = '_test_value_to_key'
        if hasattr(DummyConverter, self.key_to_value_field_name):
            del DummyConverter._test_key_to_value
        if hasattr(DummyConverter, self.value_to_key_field_name):
            del DummyConverter._test_value_to_key

    def test_get_mapping_read_file(self):
        '''Should read from file if no cache found.'''
        field_name = self.key_to_value_field_name
        self.assertIsNone(getattr(DummyConverter, field_name, None))

        # pylint: disable=protected-access
        DummyConverter._get_mapping_key_to_value()

        mapping = getattr(DummyConverter, field_name, None)
        self.assertIsNotNone(mapping)
        self.assertIsInstance(mapping, dict)
        # pylint: disable=unsubscriptable-object
        self.assertEqual(mapping['0'], 'A')
        self.assertEqual(mapping['1'], 'B')

    def test_get_key(self):
        '''Should return key.'''
        expected_key = '0'
        key = DummyConverter.get_key('A')

        self.assertEqual(key, expected_key)

    def test_get_value(self):
        '''Should return value.'''
        expected_value = 'C'
        value = DummyConverter.get_value('2')

        self.assertEqual(value, expected_value)

    def test_get_keys(self):
        '''Should return all keys.'''
        expected_keys = {'0', '1', '2'}
        keys = set(DummyConverter.get_all_keys())

        self.assertEqual(keys, expected_keys)
