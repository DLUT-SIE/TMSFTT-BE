'''Unit tests for infra pagination classes.'''
from unittest.mock import patch, Mock

from django.test import TestCase

import infra.paginations as paginations
import infra.exceptions as exceptions


class TestLimitOffsetPagination(TestCase):
    '''Unit tests for LimitOffsetPagination.'''
    def setUp(self):
        self.pagination = paginations.LimitOffsetPagination()

    @patch('rest_framework.pagination.LimitOffsetPagination.paginate_queryset')
    def test_return_paginated(self, mocked_paginate_queryset):
        '''Should return paginated queryset.'''
        paginated = Mock()
        mocked_paginate_queryset.return_value = paginated

        res = self.pagination.paginate_queryset(None, None)

        self.assertIs(res, paginated)

    @patch('rest_framework.pagination.LimitOffsetPagination.paginate_queryset')
    def test_return_none(self, mocked_paginate_queryset):
        '''Should return none if max_limit is not exceeded.'''
        mocked_paginate_queryset.return_value = None

        self.pagination.count = self.pagination.max_limit - 1
        res = self.pagination.paginate_queryset(None, None)

        self.assertIsNone(res)

    @patch('rest_framework.pagination.LimitOffsetPagination.paginate_queryset')
    def test_return_none_max_limit_exceeded(
            self, mocked_paginate_queryset):
        '''Should raise exception if max_limit is exceeded.'''
        mocked_paginate_queryset.return_value = None

        self.pagination.count = self.pagination.max_limit + 10
        with self.assertRaises(exceptions.BadRequest):
            self.pagination.paginate_queryset(None, None)

    def test_get_limit_no_query_params(self):
        '''Should return default_limit.'''
        request = Mock()
        self.pagination.limit_query_param = None
        res = self.pagination.get_limit(request)

        self.assertEqual(res, self.pagination.default_limit)

    def test_get_limit_positive_int(self):
        '''Should return limit.'''
        request = Mock()
        limit = 10
        request.query_params = {
            self.pagination.limit_query_param: f'{limit}'
        }
        res = self.pagination.get_limit(request)

        self.assertEqual(res, limit)

    def test_get_limit_none(self):
        '''Should return None if limit == '-1'.'''
        request = Mock()
        limit = -1
        request.query_params = {
            self.pagination.limit_query_param: f'{limit}'
        }
        res = self.pagination.get_limit(request)

        self.assertIsNone(res)
