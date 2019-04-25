'''Unit tests for infra middlewares.'''
from unittest.mock import patch, Mock
from django.test import TestCase

from infra.middleware import OperationLogMiddleware


class TestOperationLogMiddleware(TestCase):
    '''Unit tests for OperationLogMiddleware.'''

    def setUp(self):
        self.middleware = OperationLogMiddleware()

    @patch('infra.middleware.OperationLog.from_response')
    def test_skip_safe_request(self, mocked_from_response):
        '''Should skip creating OperationLog if it's a safe HTTP method.'''

        request = Mock()
        request.method = 'GET'

        self.middleware.process_response(request, None)

        mocked_from_response.assert_not_called()

    @patch('infra.middleware.OperationLog.from_response')
    def test_create_for_unsafe_request(self, mocked_from_response):
        '''Should create OperationLog if it's a unsafe HTTP method.'''

        request = Mock()
        request.method = 'POST'
        response = Mock()
        mocked_from_response.return_value = mocked_from_response

        self.middleware.process_response(request, response)

        mocked_from_response.assert_called_with(request, response)
        mocked_from_response.save.assert_called()
