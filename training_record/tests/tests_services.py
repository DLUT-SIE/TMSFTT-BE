'''Unit tests for training_record services.'''
import io
from django.test import TestCase
from django.contrib.auth.models import User
from django.core.files.uploadedfile import InMemoryUploadedFile
from model_mommy import mommy

from infra.exceptions import BadRequest
from training_record.models import RecordContent, RecordAttachment
from training_record.services import RecordService


class TestRecordService(TestCase):
    '''Test services provided by RecordService.'''
    @classmethod
    def setUpTestData(cls):
        cls.off_campus_event_data = {
            'name': 'abc',
            'time': '0122-12-31T15:54:17.000Z',
            'location': 'loc',
            'num_hours': 5,
            'num_participants': 30,
        }
        cls.attachments_data = [
            InMemoryUploadedFile(
                io.BytesIO(b'some content'),
                'path', 'name', 'content_type', 'size', 'charset')
            for _ in range(3)]
        cls.contents_data = [
            {'content_type': x[0], 'content': 'abc'}
            for x in RecordContent.CONTENT_TYPE_CHOICES]

    def test_create_off_campus_record_no_event_data(self):
        '''Should raise ValueError if no off-campus event data.'''
        with self.assertRaisesMessage(
                BadRequest, '校外培训活动数据格式无效'):
            RecordService.create_off_campus_record_from_raw_data()

    def test_create_off_campus_record_no_user(self):
        '''Should raise ValueError if no user.'''
        with self.assertRaisesMessage(
                BadRequest, '用户无效'):
            RecordService.create_off_campus_record_from_raw_data({})

    def test_create_off_campus_record_no_contents_and_attachments(self):
        '''Should skip extra creation if no contents or no attachments.'''
        user = mommy.make(User)

        RecordService.create_off_campus_record_from_raw_data(
            off_campus_event_data=self.off_campus_event_data,
            user=user,
            contents_data=None,
            attachments_data=None,
        )

        self.assertEqual(
            RecordContent.objects.all().count(), 0,
        )
        self.assertEqual(
            RecordAttachment.objects.all().count(), 0,
        )

    def test_create_off_campus_record(self):
        '''Should complete full creation.'''
        user = mommy.make(User)

        RecordService.create_off_campus_record_from_raw_data(
            off_campus_event_data=self.off_campus_event_data,
            user=user,
            contents_data=self.contents_data,
            attachments_data=self.attachments_data,
        )

        self.assertEqual(
            RecordContent.objects.all().count(), len(self.contents_data),
        )
        self.assertEqual(
            RecordAttachment.objects.all().count(), len(self.attachments_data),
        )
