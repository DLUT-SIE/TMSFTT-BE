'''Unit tests for auth services.'''
from django.test import TestCase

import auth.services as services


class DummyConverter(services.ChoiceConverter):
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
