'''Unit tests for secure_file fields.'''
from unittest.mock import patch, Mock
from django.test import TestCase

import secure_file.fields as fields


class TestSecureFileField(TestCase):
    '''Unit tests for SecureFileField.'''
    @patch('secure_file.fields.encrypt_file_download_url')
    def test_to_representation(self, mocked_encrypt):
        '''Should encrypt file path.'''
        name = 'path/to/file/abccc.ccc'
        encrypted = 'encrypted'
        perm_name = 'perm_name'
        value = Mock()
        value.name = name

        mocked_encrypt.return_value = encrypted

        field = fields.SecureFileField(perm_name=perm_name)
        representation = field.to_representation(value)

        self.assertDictEqual(
            representation,
            {
                'name': 'abccc.ccc',
                'url': encrypted,
            }
        )
