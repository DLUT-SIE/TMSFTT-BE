'''Unit tests for training_review models.'''
from unittest.mock import patch

from django.test import TestCase
from django.utils.text import format_lazy as _f

from training_review.models import ReviewNote


class TestReviewNote(TestCase):
    '''Unit tests for model ReviewNote.'''
    @patch('training_review.models.ReviewNote.record')
    @patch('training_review.models.ReviewNote.user')
    def test_str(self, mocked_user, mocked_record):
        '''Should render string correctly.'''
        user = 'user'
        record = 'record'
        mocked_user.__str__.return_value = user
        mocked_record.__str__.return_value = record
        expected_str = _f('由{}创建的关于{}的审核提示', user, record)

        note = ReviewNote()

        self.assertEqual(str(note), str(expected_str))
