'''Unit tests for secure_file utils.'''
from collections import OrderedDict
from unittest.mock import Mock, patch
from urllib.parse import urlencode, urljoin

from django.test import TestCase
from django.conf import settings

import secure_file.utils as utils


class TestFileDownloadURLEncryptionAndDecryption(TestCase):
    '''Unit tests for file download url encryption and decryption.'''
    @patch('secure_file.utils.encrypt')
    def test_encryption(self, mocked_encrypt):
        '''Should encrypt file download url.'''
        model_class = Mock()
        model_class._meta.app_label = 'Mock_App'
        model_class._meta.object_name = 'Mock_Class'
        model_name = (
            f'{model_class._meta.app_label}.{model_class._meta.object_name}'
        )
        field_name = 'path'
        perm_name = 'download_file'
        file_path = 'path/to/file'
        query_params = OrderedDict([
            ('model_name', model_name),
            ('field', field_name),
            ('perm', perm_name),
        ])
        encrypted_path = '<Encrypted>'
        expected_path = f'{file_path}?{urlencode(query_params)}'
        mocked_encrypt.return_value = encrypted_path

        path = utils.encrypt_file_download_url(
            model_class, field_name, file_path, perm_name)

        mocked_encrypt.assert_called_with(expected_path)
        self.assertEqual(path, urljoin(settings.MEDIA_URL, encrypted_path))

    @patch('secure_file.utils.decrypt')
    def test_decryption(self, mocked_decrypt):
        '''Should decrypt encrypted file download url.'''
        expected_path = 'path/to/file'
        expected_model_name = 'Mock_App.Mock_Class'
        expected_field_name = 'path'
        expected_perm_name = 'download_file'
        decrypted_path = (
            f'{expected_path}?model_name={expected_model_name}'
            f'&field={expected_field_name}'
            f'&perm={expected_perm_name}'
        )
        encrypted_url = '<Encrypted>'
        mocked_decrypt.return_value = decrypted_path

        model_name, field_name, path, perm_name = (
            utils.decrypt_file_download_url(encrypted_url)
        )

        mocked_decrypt.assert_called_with(encrypted_url)
        self.assertEqual(model_name, expected_model_name)
        self.assertEqual(field_name, expected_field_name)
        self.assertEqual(path, expected_path)
        self.assertEqual(perm_name, expected_perm_name)

    @patch('secure_file.utils.decrypt')
    def test_decryption_without_model_name(self, mocked_decrypt):
        '''Should raise ValueError if no model_name.'''
        expected_path = 'path/to/file'
        expected_field_name = 'path'
        expected_perm_name = 'download_file'
        decrypted_path = (
            f'{expected_path}?'
            f'&field={expected_field_name}'
            f'&perm={expected_perm_name}'
        )
        encrypted_url = '<Encrypted>'
        mocked_decrypt.return_value = decrypted_path

        with patch('secure_file.utils.dev_logger'):
            with self.assertRaisesMessage(ValueError, '参数无效'):
                utils.decrypt_file_download_url(encrypted_url)
        mocked_decrypt.assert_called_with(encrypted_url)


class TestInterContentType(TestCase):
    '''Unit tests for infer_content_type().'''
    def test_return_existing_content_type(self):
        '''Should reutrn corresponding content_type if exists.'''
        content_type = utils.infer_content_type('abccc.csv')
        self.assertEqual(content_type, 'text/csv')

    def test_return_default_content_type(self):
        '''Should return default content_type if not exists.'''
        content_type = utils.infer_content_type('abccc.not-exist')
        self.assertEqual(content_type, 'text/plain')
