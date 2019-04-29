'''Unit tests for training_record serializers.'''
import io
from unittest.mock import Mock, patch

from django.test import TestCase
from django.core.files.uploadedfile import InMemoryUploadedFile
from rest_framework import serializers
from model_mommy import mommy


from training_record.models import Record, RecordAttachment
from training_record.serializers import (
    RecordCreateSerializer, CampusEventFeedbackSerializer)
from training_event.models import OffCampusEvent


# pylint: disable=no-self-use
# pylint: disable=unused-variable
class TestRecordCreateSerializer(TestCase):
    '''Unit tests for serializer of Record.'''
    def test_validate_attachments_too_much_attachments(self):
        '''Should raise ValidationError if there are too much attachments.'''
        serializer = RecordCreateSerializer()
        off_campus_event = mommy.make(OffCampusEvent)
        files = [
            InMemoryUploadedFile(
                io.BytesIO(b'some content'),
                'path', 'name', 'content_type', 'size', 'charset')
            for _ in range(3)]
        serializer.instance = mommy.make(Record,
                                         off_campus_event=off_campus_event)
        attachments = [mommy.make(RecordAttachment, path=x,     # noqa
                                  record=serializer.instance) for x in files]
        data = [Mock() for _ in range(20)]

        with self.assertRaisesMessage(
                serializers.ValidationError, '最多允许上传3个附件'):
            serializer.validate_attachments(data)

    @patch('training_record.serializers.format_file_size',
           return_value='100 MB')
    def test_validate_attachments_data_attachments_too_large(
            self, _):
        '''
        Should raise ValidationError if the size of attachments is too large.
        '''
        serializer = RecordCreateSerializer()
        data = [Mock(size=100*1024*1024) for _ in range(2)]

        with self.assertRaisesMessage(
                serializers.ValidationError,
                '上传附件过大，请修改后再上传。(附件大小: 100 MB)'):
            serializer.validate_attachments(data)

    @patch('training_record.serializers.RecordService')
    def test_update(self, mocked_service):
        '''Should update record'''
        serializer = RecordCreateSerializer()
        serializer.update(1, {})
        mocked_service.update_off_campus_record_from_raw_data.assert_called()


class TestCampusEventFeedbackSerializer(TestCase):
    '''Unit tests for serializer of CampusEventFeedback.'''
    @patch('training_record.serializers.CampusEventFeedbackService')
    def test_create(self, mocked_service):
        '''Should create feedback'''
        serializer = CampusEventFeedbackSerializer()

        serializer.create({})

        mocked_service.create_feedback.assert_called()
