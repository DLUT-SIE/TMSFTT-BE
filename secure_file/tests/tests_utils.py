'''Unit tests for secure_file utils.'''
import os.path as osp
from collections import OrderedDict
from unittest.mock import Mock, patch
from urllib.parse import urlencode

from django.test import TestCase
from django.http import HttpResponse
from rest_framework import exceptions

from secure_file import SECURE_FILE_PREFIX, INSECURE_FILE_PREFIX
import secure_file.utils as utils


class TestSecureFileUtils(TestCase):
    '''Unit tests for utility functions.'''
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
        self.assertEqual(path, osp.join(SECURE_FILE_PREFIX, encrypted_path))

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

    def test_return_existing_content_type(self):
        '''Should reutrn corresponding content_type if exists.'''
        content_type = utils.infer_content_type('abccc.csv')
        self.assertEqual(content_type, 'text/csv')

    def test_return_default_content_type(self):
        '''Should return default content_type if not exists.'''
        content_type = utils.infer_content_type('abccc.not-exist')
        self.assertEqual(content_type, 'text/plain')

    @patch('secure_file.utils.get_full_url')
    def test_get_full_plain_file_download_url(self, mocked_get_full_url):
        '''Should return unencrypted file url.'''
        request = Mock()
        path = '/path/to/file'
        expected_path = osp.join(INSECURE_FILE_PREFIX, path)

        utils.get_full_plain_file_download_url(request, path)

        mocked_get_full_url.assert_called_with(request, expected_path)

    @patch('secure_file.utils.settings.DEBUG', True)
    def test_populate_file_content_debug_mode(self):
        '''Should read data directly in debug mode.'''
        resp = Mock()
        field_file = Mock()
        content = 'abccc'
        field_file.read.return_value = content

        utils.populate_file_content(resp, field_file)

        self.assertEqual(resp.content, content)

    @patch('secure_file.utils.settings.DEBUG', True)
    @patch('secure_file.utils.dev_logger')
    def test_populate_file_content_debug_mode_fail(self, _):
        '''Should raise NotFound error.'''
        resp = Mock()
        field_file = Mock()
        field_file.read.side_effect = Exception

        with self.assertRaises(exceptions.NotFound):
            utils.populate_file_content(resp, field_file)

    @patch('secure_file.utils.settings.DEBUG', False)
    def test_populate_file_content_prod_mode(self):
        '''Should set X-Accel-Redirect header.'''
        resp = {}
        field_file = Mock()
        field_file.name = 'path/to/file'
        expected_path = f'/protected-files/{field_file.name}'

        utils.populate_file_content(resp, field_file)

        self.assertEqual(resp['X-Accel-Redirect'], expected_path)

    @patch('secure_file.utils.prod_logger.info')
    @patch('secure_file.utils.infer_content_type')
    @patch('secure_file.utils.populate_file_content')
    def test_generate_download_response(
            self, mocked_populate_file_content, mocked_infer_content_type,
            mocked_info):
        '''Should return response.'''
        mocked_infer_content_type.return_value = 'image/png'
        request = Mock()
        field_file = Mock()
        field_file.name = 'path/to/file.abc'
        expected_content_disposition = f'attachment; filename=file.abc'

        resp = utils.generate_download_response(request, field_file)

        self.assertIsInstance(resp, HttpResponse)
        self.assertEqual(resp['Content-Disposition'],
                         expected_content_disposition)
        mocked_infer_content_type.assert_called_with('file.abc')
        mocked_populate_file_content.assert_called_with(resp, field_file)
        mocked_info.assert_called()
