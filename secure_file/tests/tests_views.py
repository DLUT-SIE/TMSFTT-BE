'''Unit tests for secure_file views.'''
from unittest.mock import patch, Mock
from urllib.parse import unquote, quote

from django.test import TestCase
from rest_framework import exceptions

import secure_file.views as views


# pylint: disable=too-many-arguments
class TestSecuredFileDownloadView(TestCase):
    '''Unit tests for SecuredFileDownloadView.'''
    def setUp(self):
        self.view = views.SecuredFileDownloadView()
        self.request = Mock()
        self.encrypted_url = '/media/encrypted'
        self.model_name = 'App.Model'
        self.field_name = 'path'
        self.path = 'path/to/file'
        self.perm_name = 'download_file'

    @patch('secure_file.views.decrypt_file_download_url')
    def test_get_decryption_failed(self, mocked_decrypt):
        '''Should raise NotFound() if decryption failed.'''
        mocked_decrypt.side_effect = Exception('Failed to decrypt!')
        with self.assertRaises(exceptions.NotFound):
            self.view.get(self.request, self.encrypted_url)

    @patch('secure_file.views.settings')
    @patch('secure_file.views.infer_content_type')
    @patch('secure_file.views.prod_logger')
    @patch('secure_file.views.decrypt_file_download_url')
    @patch('secure_file.views.SecuredFileDownloadView._verify_validity')
    def test_get_succeed(self, mocked_verify, mocked_decrypt,
                         mocked_logger, mocked_infer_content_type,
                         mocked_settings):
        '''Should return response if succeed.'''
        mocked_decrypt.return_value = (
            self.model_name, self.field_name, self.path, self.perm_name
        )
        field_file = Mock()
        basename = 'abc.png'
        content = b'Hello World!'
        field_file.name = f'path/to/file/{basename}'
        field_file.read.return_value = content
        mocked_verify.return_value = field_file
        mocked_infer_content_type.reutrn_value = 'image/png'
        self.request.user.first_name = 'first_name'
        self.request.user.username = 'username'

        mocked_settings.DEBUG = True
        response = self.view.get(self.request, self.encrypted_url)

        self.assertEqual(
            response['Content-Disposition'],
            f'attachment; filename={quote(basename)}'
        )
        self.assertEqual(
            response.content, content,
        )
        mocked_logger.info.assert_called_with(
            f'用户 {self.request.user.first_name}'
            f'(用户名: {self.request.user.username}) '
            f'请求下载文件: {unquote(self.path)}'
        )
        mocked_infer_content_type.assert_called_with(basename)
        mocked_verify.assert_called_with(
            self.request, self.model_name, self.field_name,
            self.path, self.perm_name
        )

    @patch('secure_file.views.settings')
    @patch('secure_file.views.infer_content_type')
    @patch('secure_file.views.dev_logger')
    @patch('secure_file.views.prod_logger')
    @patch('secure_file.views.decrypt_file_download_url')
    @patch('secure_file.views.SecuredFileDownloadView._verify_validity')
    def test_get_read_failed(self, mocked_verify, mocked_decrypt,
                             mocked_prod_logger, mocked_dev_logger,
                             mocked_infer_content_type, mocked_settings):
        '''Should raise NotFound() if read failed.'''
        mocked_decrypt.return_value = (
            self.model_name, self.field_name, self.path, self.perm_name
        )
        field_file = Mock()
        basename = 'abc.png'
        field_file.name = f'path/to/file/{basename}'
        exc = Exception('Failed to read')
        field_file.read.side_effect = exc
        mocked_verify.return_value = field_file
        mocked_infer_content_type.reutrn_value = 'image/png'
        self.request.user.first_name = 'first_name'
        self.request.user.username = 'username'

        mocked_settings.DEBUG = True
        with self.assertRaises(exceptions.NotFound):
            self.view.get(self.request, self.encrypted_url)

        mocked_dev_logger.info.assert_called_with(f'读取文件失败: {exc}')
        mocked_prod_logger.info.assert_called_with(
            f'用户 {self.request.user.first_name}'
            f'(用户名: {self.request.user.username}) '
            f'请求下载文件: {unquote(self.path)}'
        )
        mocked_infer_content_type.assert_called_with(basename)
        mocked_verify.assert_called_with(
            self.request, self.model_name, self.field_name,
            self.path, self.perm_name
        )

    @patch('secure_file.views.settings')
    @patch('secure_file.views.infer_content_type')
    @patch('secure_file.views.prod_logger')
    @patch('secure_file.views.decrypt_file_download_url')
    @patch('secure_file.views.SecuredFileDownloadView._verify_validity')
    def test_get_succeed_acceel_redirect(
            self, mocked_verify, mocked_decrypt,
            mocked_logger, mocked_infer_content_type, mocked_settings):
        '''Should return redirect response if succeed in prod mode.'''
        mocked_decrypt.return_value = (
            self.model_name, self.field_name, self.path, self.perm_name
        )
        field_file = Mock()
        basename = 'abc.png'
        content = b'Hello World!'
        field_file.name = f'path/to/file/{basename}'
        field_file.read.return_value = content
        mocked_verify.return_value = field_file
        mocked_infer_content_type.reutrn_value = 'image/png'
        self.request.user.first_name = 'first_name'
        self.request.user.username = 'username'

        mocked_settings.DEBUG = False
        response = self.view.get(self.request, self.encrypted_url)

        self.assertEqual(
            response['Content-Disposition'],
            f'attachment; filename={quote(basename)}'
        )
        self.assertEqual(
            response['X-Accel-Redirect'],
            f'/protected-files/{field_file.name}'
        )
        mocked_logger.info.assert_called_with(
            f'用户 {self.request.user.first_name}'
            f'(用户名: {self.request.user.username}) '
            f'请求下载文件: {unquote(self.path)}'
        )
        mocked_infer_content_type.assert_called_with(basename)
        mocked_verify.assert_called_with(
            self.request, self.model_name, self.field_name,
            self.path, self.perm_name
        )

    @patch('secure_file.views.dev_logger')
    @patch('secure_file.views.apps')
    @patch('secure_file.views.get_object_or_404')
    def test_verify_validity_file_mismatch(
            self, mocked_get_object, mocked_apps, mocked_logger):
        '''Should raise NotFound() if file mismatch.'''
        real_file = Mock()
        real_file.name = self.path + 'mismatch-suffix'
        instance = Mock()
        setattr(instance, self.field_name, real_file)
        mocked_get_object.return_value = instance
        mocked_apps.get_model.return_value = None

        with self.assertRaises(exceptions.NotFound):
            self.view._verify_validity(  # pylint: disable=protected-access
                self.request, self.model_name,
                self.field_name, self.path, self.perm_name)

        mocked_apps.get_model.assert_called_with(self.model_name)
        mocked_logger.info.assert_called_with(
            f'文件路径无效: {self.path}'
        )
        mocked_get_object.assert_called_with(
            None, **{self.field_name: self.path}
        )

    @patch('secure_file.views.prod_logger')
    @patch('secure_file.views.apps')
    @patch('secure_file.views.get_object_or_404')
    def test_verify_validity_no_permission(
            self, mocked_get_object, mocked_apps, mocked_logger):
        '''Should raise NotFound() if no permission.'''
        real_file = Mock()
        real_file.name = self.path
        instance = Mock()
        setattr(instance, self.field_name, real_file)
        mocked_get_object.return_value = instance
        mocked_apps.get_model.return_value = None
        self.request.user.has_perm.return_value = False

        with self.assertRaises(exceptions.NotFound):
            self.view._verify_validity(  # pylint: disable=protected-access
                self.request, self.model_name,
                self.field_name, self.path, self.perm_name)

        mocked_apps.get_model.assert_called_with(self.model_name)
        mocked_logger.info.assert_called_with(
            f'用户 {self.request.user.first_name}'
            f'(用户名: {self.request.user.username}) '
            f'尝试访问无权限文件: {self.path}'
        )
        mocked_get_object.assert_called_with(
            None, **{self.field_name: self.path}
        )
        self.request.user.has_perm.assert_called_with(
            self.perm_name, instance
        )

    @patch('secure_file.views.apps')
    @patch('secure_file.views.get_object_or_404')
    def test_verify_validity_return_real_file(
            self, mocked_get_object, mocked_apps):
        '''Should return real file if request is valid.'''
        expected_real_file = Mock()
        expected_real_file.name = self.path
        instance = Mock()
        setattr(instance, self.field_name, expected_real_file)
        mocked_get_object.return_value = instance
        mocked_apps.get_model.return_value = None
        self.request.user.has_perm.return_value = True

        # pylint: disable=protected-access
        real_file = self.view._verify_validity(
            self.request, self.model_name,
            self.field_name, self.path, self.perm_name)

        self.assertIs(real_file, expected_real_file)
        mocked_apps.get_model.assert_called_with(self.model_name)
        mocked_get_object.assert_called_with(
            None, **{self.field_name: self.path}
        )
        self.request.user.has_perm.assert_called_with(
            self.perm_name, instance
        )
