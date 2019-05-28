'''Unit tests for training_record serializers.'''
import io
from unittest.mock import Mock, patch

from django.test import TestCase
from django.core.files.uploadedfile import InMemoryUploadedFile
from rest_framework import serializers
from model_mommy import mommy

from infra.exceptions import BadRequest
from training_record.models import Record, RecordAttachment
from training_record.serializers import (
    RecordWriteSerializer, CampusEventFeedbackSerializer)
from training_event.models import OffCampusEvent


# pylint: disable=no-self-use
# pylint: disable=unused-variable
class TestRecordWriteSerializer(TestCase):
    '''Unit tests for serializer of Record.'''
    @patch('os.path.splitext', lambda x: ('abc', '.pdf'))
    def test_validate_attachments_too_much_attachments(self):
        '''Should raise ValidationError if there are too much attachments.'''
        serializer = RecordWriteSerializer()
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

    @patch('os.path.splitext', lambda x: ('abc', '.pdf'))
    @patch('training_record.serializers.format_file_size',
           return_value='100 MB')
    def test_validate_attachments_data_attachments_too_large(
            self, _):
        '''
        Should raise ValidationError if the size of attachments is too large.
        '''
        serializer = RecordWriteSerializer()
        data = [Mock(size=100*1024*1024, name='a.png') for _ in range(2)]

        with self.assertRaisesMessage(
                serializers.ValidationError,
                '上传附件过大，请修改后再上传。(附件大小: 100 MB)'):
            serializer.validate_attachments(data)

    @patch('training_record.serializers.RecordService')
    def test_update(self, mocked_service):
        '''Should update record'''
        serializer = RecordWriteSerializer()
        serializer.update(1, {})
        mocked_service.update_off_campus_record_from_raw_data.assert_called()

    def test_validate_with_bad_data(self):
        '''shoud raise badrequest when have no right'''
        off_campus_event = mommy.make(OffCampusEvent)
        record = mommy.make(Record, off_campus_event=off_campus_event)
        request = Mock()
        user = Mock()
        user.is_school_admin = False
        user.is_teacher = False
        request.user = user
        context = {
            'request': request
        }
        serializer = RecordWriteSerializer(record, context=context)
        serializer.instance = Mock()
        with self.assertRaisesMessage(
                BadRequest,
                '在此状态下您无法更改。'):
            serializer.validate('')


class TestCampusEventFeedbackSerializer(TestCase):
    '''Unit tests for serializer of CampusEventFeedback.'''
    @patch('training_record.serializers.CampusEventFeedbackService')
    def test_create(self, mocked_service):
        '''Should create feedback'''
        serializer = CampusEventFeedbackSerializer()

        serializer.create({})

        mocked_service.create_feedback.assert_called()

    def test_validate_with_bad_permission(self):
        '''should raise bad request when have no right'''
        request = Mock()
        user = Mock()
        user.has_perm = Mock(return_value=False)
        request.user = user
        context = {
            'request': request
        }
        serializer = CampusEventFeedbackSerializer(context=context)
        with self.assertRaisesMessage(
                BadRequest,
                '您没有权限为此记录提交反馈'):
            serializer.validate({'record': '1'})
