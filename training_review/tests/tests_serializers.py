'''Unit tests for training_review serializers.'''
from unittest.mock import Mock

from django.test import TestCase
from rest_framework import serializers

from training_review.serializers import ReviewNoteSerializer


class TestReviewNoteSerializer(TestCase):
    '''Unit tests for serializer of ReviewNote.'''
    def test_validate(self):
        '''
        Should raise ValidationError if
        user doesn't have permission to change record.
        '''
        review_note = Mock()
        request = Mock()
        user = Mock()
        request.user = user
        context = {
            'request': request
        }
        serializer = ReviewNoteSerializer(review_note, context=context)
        with self.assertRaises(serializers.ValidationError):
            serializer.validate({})
