'''Unit tests for auth permission checkers.'''
from unittest.mock import Mock

from django.test import TestCase

from auth.permissions import CurrentUser


class TestCurrentUserChecker(TestCase):
    '''Unit tests for CurrentUser checker.'''

    @classmethod
    def setUpTestData(cls):
        cls.checker = CurrentUser()

    def test_no_kwargs(self):
        '''Should return False if no kwargs.'''
        request = Mock()
        request.parser_context = {}

        has_perm = self.checker.has_permission(request, None)

        self.assertFalse(has_perm)

    def test_no_user_pk(self):
        '''Should return False if no user pk in kwargs.'''
        request = Mock()
        request.parser_context = {
            'kwargs': {},
        }

        has_perm = self.checker.has_permission(request, None)

        self.assertFalse(has_perm)

    def test_not_match(self):
        '''Should return False if user pks don't match.'''
        request = Mock()
        user_pk = 1
        request.parser_context = {
            'kwargs': {
                'user_pk': user_pk,
            },
        }
        request.user.pk = user_pk + 1

        has_perm = self.checker.has_permission(request, None)

        self.assertFalse(has_perm)

    def test_match(self):
        '''Should return True if user pks match.'''
        request = Mock()
        user_pk = 1
        request.parser_context = {
            'kwargs': {
                'user_pk': user_pk,
            },
        }
        request.user.pk = user_pk

        has_perm = self.checker.has_permission(request, None)

        self.assertTrue(has_perm)
