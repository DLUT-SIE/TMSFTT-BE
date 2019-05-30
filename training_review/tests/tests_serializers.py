'''Unit tests for training_review serializers.'''
from unittest.mock import Mock, patch

from django.test import TestCase
from rest_framework import serializers

from training_review.serializers import ReviewNoteSerializer


class TestReviewNoteSerializer(TestCase):
    '''Unit tests for serializer of ReviewNote.'''
    @patch('training_review.serializers.ReviewNoteService')
    def test_create(self, mocked_service):
        '''Should create feedback'''
        request = Mock()
        user = Mock()
        request.user = user
        context = {
            'request': request
        }
        serializer = ReviewNoteSerializer(context=context)

        serializer.create({})

        mocked_service.create_review_note.assert_called()

    def test_validate_no_permission(self):
        '''
        Should raise ValidationError if
        user doesn't have permission to change record.
        '''
        request = Mock()
        user = Mock()
        user.has_perm = Mock(return_value=False)
        request.user = user
        context = {
            'request': request
        }
        serializer = ReviewNoteSerializer(context=context)
        with self.assertRaisesMessage(serializers.ValidationError,
                                      '您无权添加审核提示！'):
            serializer.validate({'record': 1, 'content': 'a'})

    def test_validate_has_permission(self):
        '''
        Should return data if user
        has permission to change record.
        '''
        request = Mock()
        user = Mock()
        user.has_perm = Mock(return_value=True)
        request.user = user
        context = {
            'request': request
        }
        data = {'record': 1, 'content': 'a'}
        serializer = ReviewNoteSerializer(data, context=context)
        result = serializer.validate({})

        self.assertIsInstance(result, dict)
