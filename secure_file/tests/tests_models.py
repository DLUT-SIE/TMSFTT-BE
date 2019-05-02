'''Unit tests for secure_file models.'''
import os
import tempfile
from unittest.mock import patch, Mock

from django.test import TestCase
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from model_mommy import mommy
from rest_framework import status

from secure_file.models import SecureFile


class TestSecureFile(TestCase):
    '''Unit tests for SecureFile model.'''
    @classmethod
    def setUpTestData(cls):
        cls.user = mommy.make(get_user_model())

    def test_create_instance_from_system_path(self):
        '''Should create when given path to file.'''
        handle, fpath = tempfile.mkstemp()
        content = b'Hello World!\n'
        with open(handle, 'wb') as opened_file:
            opened_file.write(content)
        secure_file = SecureFile.from_path(self.user, 'fname', fpath)
        os.remove(fpath)
        self.assertEqual(secure_file.path.read(), content)

    def test_create_instance_from_in_memory_file(self):
        '''Should create when given an InMemoryFile.'''
        content = b'Hello World!\n'
        in_memory_file = SimpleUploadedFile('fname', content)
        secure_file = SecureFile.from_path(self.user, 'fname', in_memory_file)
        self.assertEqual(secure_file.path.read(), content)

    @patch('secure_file.models.get_full_encrypted_file_download_url')
    def test_generate_secured_download_response(self, mocked_get_url):
        '''Should generate response for redirecting to download.'''
        secure_file = SecureFile()
        secure_file.path = Mock()
        path = 'path/to/file'
        secure_file.path.name = path
        expected_url = Mock()
        mocked_get_url.return_value = expected_url
        request = Mock()
        resp = secure_file.generate_secured_download_response(request)

        mocked_get_url.assert_called_with(
            request, SecureFile, 'path', path, 'download_file'
        )

        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        self.assertIn('url', resp.data)
        self.assertEqual(resp.data['url'], expected_url)
