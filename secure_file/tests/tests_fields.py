'''Unit tests for secure_file fields.'''
from unittest.mock import patch, Mock
from django.test import TestCase

import secure_file.fields as fields


class TestSecureFileField(TestCase):
    '''Unit tests for SecureFileField.'''
    @patch('secure_file.fields.get_full_encrypted_file_download_url')
    def test_to_representation(self, mocked_get_url):
        '''Should encrypt file path.'''
        name = 'path/to/file/abccc.ccc'
        expected_url = 'expected-url'
        perm_name = 'perm_name'
        value = Mock()
        value.name = name
        request = Mock()

        mocked_get_url.return_value = expected_url

        field = fields.SecureFileField(perm_name=perm_name)
        field._context = {  # pylint: disable=protected-access
            'request': request,
        }

        representation = field.to_representation(value)

        mocked_get_url.assert_called_with(
            request, value.field.model, field.source, value.name,
            field.perm_name
        )
        self.assertDictEqual(
            representation,
            {
                'name': 'abccc.ccc',
                'url': expected_url,
            }
        )
