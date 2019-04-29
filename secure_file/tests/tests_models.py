'''Unit tests for secure_file models.'''
import os
import tempfile
from unittest.mock import patch, Mock
from urllib.parse import urlunsplit

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

    @patch('secure_file.models.get_current_site')
    @patch('secure_file.models.encrypt_file_download_url')
    def test_generate_secured_download_response(
            self, mocked_encrypt, mocked_get_current_site):
        '''Should generate response for redirecting to download.'''
        secure_file = SecureFile()
        secure_file.path = Mock()
        path = 'path/to/file'
        secure_file.path.name = path
        encrypted_url = '/media/Encrypted'
        current_site = Mock()
        current_site.domain = 'http://localhost:8000'
        mocked_encrypt.return_value = encrypted_url
        mocked_get_current_site.return_value = current_site
        request = Mock()
        request.scheme = 'http'
        expected_url = urlunsplit((
            request.scheme,  # URL scheme specifier
            current_site.domain,  # Network location part
            encrypted_url,  # Hierarchical path
            '',  # Query component
            ''  # Fragment identifier
        ))

        resp = secure_file.generate_secured_download_response(request)

        mocked_encrypt.assert_called_with(
            SecureFile, 'path', path, 'download_file'
        )

        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        self.assertIn('url', resp.data)
        self.assertEqual(resp.data['url'], expected_url)
