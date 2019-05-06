'''Unit tests for secure_file views.'''
from unittest.mock import patch, Mock

from django.test import TestCase
from rest_framework import exceptions
from model_mommy import mommy

from infra.exceptions import BadRequest
import secure_file.views as views
import secure_file.models as models


class TestInSecuredFileDownloadView(TestCase):
    '''Unit tests for INSecureFileDownloadView.'''
    def setUp(self):
        self.view = views.InSecuredFileDownloadView()
        self.request = Mock()

    def test_invalid_id(self):
        '''Should raise NotFound error.'''
        file_id = 'abc'

        with self.assertRaises(exceptions.NotFound):
            self.view.get(self.request, file_id)

    def test_file_does_not_exist(self):
        '''Should raise NotFound error.'''
        file_id = '123123'

        with self.assertRaises(exceptions.NotFound):
            self.view.get(self.request, file_id)

    @patch('secure_file.views.generate_download_response')
    def test_get_succeed(self, mocked_generate):
        '''Should return response.'''
        insecure_file = mommy.make(models.InSecureFile)
        expected_resp = Mock()
        mocked_generate.return_value = expected_resp

        resp = self.view.get(self.request, str(insecure_file.id))

        self.assertIs(resp, expected_resp)
        mocked_generate.assert_called_with(
            self.request, insecure_file.path, logging=False
        )


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

    @patch('secure_file.views.SecuredFileDownloadView._verify_validity')
    @patch('secure_file.views.generate_download_response')
    @patch('secure_file.views.decrypt_file_download_url')
    def test_get_succeed(self, mocked_decrypt, mocked_generate, mocked_verify):
        '''Should return response.'''
        model_name = 'abc'
        field_name = 'path'
        path = 'path/to/file'
        perm_name = 'download'
        mocked_decrypt.return_value = (model_name, field_name, path, perm_name)
        field_file = Mock()
        mocked_verify.return_value = field_file
        expected_res = Mock()
        mocked_generate.return_value = expected_res

        res = self.view.get(self.request, self.encrypted_url)

        self.assertIs(res, expected_res)
        mocked_decrypt.assert_called_with(self.encrypted_url)
        mocked_verify.assert_called_with(
            self.request, model_name, field_name, path, perm_name
        )
        mocked_generate.assert_called_with(self.request, field_file)

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


class TestInSecureFileViewSet(TestCase):
    '''Unit tests for InSecureFileViewSet.'''
    def setUp(self):
        self.view = views.InSecureFileViewSet()
        self.request = Mock()

    def test_create_key_missing(self):
        '''Should raise BadRequest.'''
        request = self.request
        request.FILES = {}
        with self.assertRaisesMessage(BadRequest, '请指定上传文件'):
            self.view.create(request)

    @patch('secure_file.models.InSecureFile.from_path')
    def test_create_file(self, mocked_from_path):
        '''Should create InSecureFile.'''
        request = self.request
        request.user = Mock()
        uploaded_file = Mock()
        uploaded_file.name = 'name'
        request.FILES = {
            'upload': uploaded_file
        }
        mocked_generate = Mock()
        expected_resp = Mock()
        mocked_generate.return_value = expected_resp
        insecure_file = Mock()
        insecure_file.generate_download_response = mocked_generate
        mocked_from_path.return_value = insecure_file

        resp = self.view.create(request)

        self.assertIs(resp, expected_resp)
        mocked_from_path.assert_called_with(
            request.user, uploaded_file.name, uploaded_file
        )
        mocked_generate.assert_called_with(request)
