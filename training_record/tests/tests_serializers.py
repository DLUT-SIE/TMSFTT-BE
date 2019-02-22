'''Unit tests for training_record serializers.'''
from unittest.mock import patch, Mock

from django.test import TestCase

import training_record.serializers as serializers


class TestRecordAttachmentSerializer(TestCase):
    '''Unit tests for serializer of RecordAttachment.'''
    @patch('training_record.serializers.infer_attachment_type')
    def test_infer_attachment_type_in_validate(self, mocked_func):
        '''Should set attachment_type.'''
        serializer = serializers.RecordAttachmentSerializer()

        attrs = serializer.validate({
            'record': 1,
            'path': Mock(),
        })

        mocked_func.assert_called()
        self.assertIn('attachment_type', attrs)
