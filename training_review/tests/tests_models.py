from unittest.mock import patch

from django.test import TestCase
from django.utils.translation import gettext_lazy as _

from training_review.models import ReviewNote


class TestReviewNote(TestCase):
    @patch('training_review.models.ReviewNote.record')
    @patch('training_review.models.ReviewNote.user')
    def test_str(self, mocked_user, mocked_record):
        user = 'user'
        record = 'record'
        mocked_user.__str__.return_value = user
        mocked_record.__str__.return_value = record
        expected_str = _('由{}创建的关于{}的审核提示').format(
            user, record)

        note = ReviewNote()

        self.assertEqual(str(note), expected_str)
