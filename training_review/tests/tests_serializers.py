'''Unit tests for training_review serializers.'''
from django.test import TestCase

import training_review.serializers as serializers
import training_review.models as models


class TestReviewNoteSerializer(TestCase):
    '''Unit tests for serializer of ReviewNote.'''
    def test_fields_equal(self):
        '''Serializer should return fields of ReviewNote correctly.'''
        review_note = models.ReviewNote()
        expected_keys = {'id', 'create_time', 'record', 'field_name',
                         'user', 'content'}

        keys = set(serializers.ReviewNoteSerializer(review_note).data.keys())
        self.assertEqual(keys, expected_keys)
