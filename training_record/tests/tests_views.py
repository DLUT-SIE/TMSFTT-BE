'''Unit tests for training_record views.'''
import io
import tempfile
import json
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import override_settings
from django.urls import reverse
from django.utils.timezone import now
from model_mommy import mommy
from rest_framework import status
from rest_framework.test import APITestCase

import training_record.models
from training_record.models import (
    Record, RecordContent, RecordAttachment, StatusChangeLog)
import training_event.models


User = get_user_model()


class TestRecordViewSet(APITestCase):
    '''Unit tests for Record view.'''
    @classmethod
    def setUpTestData(cls):
        cls.user = mommy.make(User)

    def setUp(self):
        self.client.force_authenticate(self.user)

    def test_create_record(self):
        '''Record should be created by POST request.'''
        user = mommy.make(User)
        url = reverse('record-list')
        off_campus_event_data = {
            'name': 'abc',
            'time': '0122-12-31T15:54:17.000Z',
            'location': 'loc',
            'num_hours': 5,
            'num_participants': 30,
        }
        attachments_data = [io.BytesIO(b'some content') for _ in range(3)]
        contents_data = [
            json.dumps({'content_type': x[0], 'content': 'abc'})
            for x in RecordContent.CONTENT_TYPE_CHOICES]
        data = {
            'off_campus_event_data': json.dumps(off_campus_event_data),
            'user': user.id,
            'contents_data': contents_data,
            'attachments_data': attachments_data,
        }

        response = self.client.post(url, data, format='multipart')
        event = training_event.models.OffCampusEvent.objects.get()

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(training_record.models.Record.objects.count(), 1)
        self.assertEqual(
            training_record.models.Record.objects.get().off_campus_event.id,
            event.id)
        self.assertEqual(
            training_record.models.Record.objects.get().user.id, user.id)

    def test_list_record(self):
        '''Record list should be accessed by GET request.'''
        url = reverse('record-list')

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_list_reviewed_record(self):
        '''should return records which are already reviewed.'''
        url = reverse('record-reviewed')
        for index in range(10):
            off_campus_event = mommy.make(training_event.models.OffCampusEvent)
            mommy.make(Record,
                       off_campus_event=off_campus_event,
                       status=Record.STATUS_SCHOOL_ADMIN_REVIEWED
                       if index % 4 == 0 else Record.STATUS_SUBMITTED)

        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 3)

    @patch('training_record.views.RecordViewSet.paginate_queryset')
    def test_return_full_if_no_pagination(self, mocked_paginate):
        '''should return full page if no pagination is required.'''
        url = reverse('record-reviewed')

        mocked_paginate.return_value = None

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_delete_record(self):
        '''Record should be deleted by DELETE request.'''
        campus_event = mommy.make(training_event.models.CampusEvent)
        record = mommy.make(training_record.models.Record,
                            campus_event=campus_event)
        url = reverse('record-detail', args=(record.pk,))

        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(training_record.models.Record.objects.count(), 0)

    def test_get_record(self):
        '''Record should be accessed by GET request.'''
        campus_event = mommy.make(training_event.models.CampusEvent)
        record = mommy.make(training_record.models.Record,
                            campus_event=campus_event)
        url = reverse('record-detail', args=(record.pk,))
        expected_keys = {'id', 'create_time', 'update_time', 'campus_event',
                         'off_campus_event', 'user', 'status', 'contents',
                         'attachments', 'status_str', 'role', 'feedback'}

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(set(response.data.keys()), expected_keys)

    def test_update_record(self):
        '''Record should be updated by PATCH request.'''
        status0 = training_record.models.Record.STATUS_SUBMITTED
        status1 = training_record.models.Record.STATUS_FACULTY_ADMIN_REVIEWED
        campus_event = mommy.make(training_event.models.CampusEvent)
        record = mommy.make(training_record.models.Record,
                            campus_event=campus_event, status=status0)
        url = reverse('record-detail', args=(record.pk,))
        data = {'status': status1}

        response = self.client.patch(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('status', response.data)
        self.assertEqual(response.data['status'], status1)


class TestRecordActionViewSet(APITestCase):
    '''Unit tests for RecordActionViewSet'''

    @patch('training_record.views.RecordService')
    def test_batch_submit(self, mocked_service):
        '''Should batch create records according to request.'''
        user = mommy.make(get_user_model())
        url = reverse('record-actions-batch-submit')
        file_data = io.BytesIO(b'some numbers')
        mocked_service.create_campus_records_from_excel.return_value = 3

        self.client.force_authenticate(user)
        response = self.client.post(url, {'file': file_data})

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('count', response.data)


class TestRecordContentViewSet(APITestCase):
    '''Unit tests for RecordContent view.'''
    @classmethod
    def setUpTestData(cls):
        cls.user = mommy.make(User)

    def setUp(self):
        self.client.force_authenticate(self.user)

    def test_create_record_content(self):
        '''RecordContent should be created by POST request.'''
        url = reverse('recordcontent-list')

        campus_event = mommy.make(training_event.models.CampusEvent)
        record = mommy.make(training_record.models.Record,
                            campus_event=campus_event)
        content_type = RecordContent.CONTENT_TYPE_CONTENT
        content = "ABC"
        data = {'record': record.id, 'content_type': content_type,
                'content': content}

        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(
            training_record.models.RecordContent.objects.count(), 1)
        self.assertEqual(
            training_record.models.RecordContent.objects.get().record.id,
            record.id)
        self.assertEqual(
            training_record.models.RecordContent.objects.get().content_type,
            content_type)
        self.assertEqual(
            training_record.models.RecordContent.objects.get().content,
            content)

    def test_list_record_content(self):
        '''RecordContent list should be accessed by GET request.'''
        url = reverse('recordcontent-list')

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_delete_record_content(self):
        '''RecordContent should be deleted by DELETE request.'''
        campus_event = mommy.make(training_event.models.CampusEvent)
        record = mommy.make(training_record.models.Record,
                            campus_event=campus_event)
        record_content = mommy.make(training_record.models.RecordContent,
                                    record=record)
        url = reverse('recordcontent-detail', args=(record_content.pk,))

        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(
            training_record.models.RecordContent.objects.count(), 0)

    def test_get_record_content(self):
        '''RecordContent should be accessed by GET request.'''
        campus_event = mommy.make(training_event.models.CampusEvent)
        record = mommy.make(training_record.models.Record,
                            campus_event=campus_event)
        record_content = mommy.make(training_record.models.RecordContent,
                                    record=record)
        url = reverse('recordcontent-detail', args=(record_content.pk,))
        expected_keys = {'id', 'create_time', 'update_time', 'record',
                         'content_type', 'content'}

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(set(response.data.keys()), expected_keys)

    def test_update_record_content(self):
        '''RecordContent should be updated by PATCH request.'''
        content_type0 = RecordContent.CONTENT_TYPE_CONTENT
        content_type1 = RecordContent.CONTENT_TYPE_SUMMARY
        campus_event = mommy.make(training_event.models.CampusEvent)
        record = mommy.make(training_record.models.Record,
                            campus_event=campus_event)
        record_content = mommy.make(training_record.models.RecordContent,
                                    record=record, content_type=content_type0)
        url = reverse('recordcontent-detail', args=(record_content.pk,))
        data = {'content_type': content_type1}

        response = self.client.patch(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('content_type', response.data)
        self.assertEqual(response.data['content_type'], content_type1)


@override_settings(MEDIA_ROOT=tempfile.gettempdir())
class TestRecordAttachmentViewSet(APITestCase):
    '''Unit tests for RecordAttachment view.'''
    @classmethod
    def setUpTestData(cls):
        cls.user = mommy.make(User)

    def setUp(self):
        self.client.force_authenticate(self.user)

    def test_create_record_attachment(self):
        '''RecordAttachment should be created by POST request.'''
        url = reverse('recordattachment-list')
        campus_event = mommy.make(training_event.models.CampusEvent)
        record = mommy.make(training_record.models.Record,
                            campus_event=campus_event)
        attachment_type = RecordAttachment.ATTACHMENT_TYPE_CONTENT
        path = io.BytesIO(b'some content')
        data = {'record': record.id, 'attachment_type': attachment_type,
                'path': path}

        response = self.client.post(url, data, format='multipart')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(RecordAttachment.objects.count(), 1)
        self.assertEqual(RecordAttachment.objects.get().record.id, record.id)
        self.assertEqual(RecordAttachment.objects.get().attachment_type,
                         attachment_type)

    def test_list_record_attachment(self):
        '''RecordAttachment list should be accessed by GET request.'''
        url = reverse('recordattachment-list')

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_delete_record_attachment(self):
        '''RecordAttachment should be deleted by DELETE request.'''
        campus_event = mommy.make(training_event.models.CampusEvent)
        record = mommy.make(training_record.models.Record,
                            campus_event=campus_event)
        record_attachment = mommy.make(training_record.models.RecordAttachment,
                                       record=record)
        url = reverse('recordattachment-detail', args=(record_attachment.pk,))

        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(RecordAttachment.objects.count(), 0)

    def test_get_record_attachment(self):
        '''RecordAttachment should be accessed by GET request.'''
        campus_event = mommy.make(training_event.models.CampusEvent)
        record = mommy.make(training_record.models.Record,
                            campus_event=campus_event)
        record_attachment = mommy.make(training_record.models.RecordAttachment,
                                       record=record)
        url = reverse('recordattachment-detail', args=(record_attachment.pk,))
        expected_keys = {'id', 'create_time', 'update_time', 'record',
                         'attachment_type', 'path'}

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(set(response.data.keys()), expected_keys)

    def test_update_record_attachment(self):
        '''RecordAttachment should be updated by PATCH request.'''
        attachment_type0 = RecordAttachment.ATTACHMENT_TYPE_CONTENT
        attachment_type1 = RecordAttachment.ATTACHMENT_TYPE_SUMMARY
        campus_event = mommy.make(training_event.models.CampusEvent)
        record = mommy.make(training_record.models.Record,
                            campus_event=campus_event)
        record_attachment = mommy.make(
            training_record.models.RecordAttachment, record=record,
            attachment_type=attachment_type0)
        url = reverse('recordattachment-detail', args=(record_attachment.pk,))
        data = {'attachment_type': attachment_type1}

        response = self.client.patch(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('attachment_type', response.data)
        self.assertEqual(response.data['attachment_type'], attachment_type1)


class TestStatusChangeLogViewSet(APITestCase):
    '''Unit tests for StatusChangeLog view.'''
    @classmethod
    def setUpTestData(cls):
        cls.user = mommy.make(User)

    def setUp(self):
        self.client.force_authenticate(self.user)

    def test_create_status_change_log(self):
        '''StatusChangeLog should be created by POST request.'''
        url = reverse('statuschangelog-list')

        campus_event = mommy.make(training_event.models.CampusEvent)
        record = mommy.make(training_record.models.Record,
                            campus_event=campus_event)
        user = mommy.make(User)
        time = now()
        data = {'user': user.id, 'time': time, 'record': record.id}

        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(StatusChangeLog.objects.count(), 1)
        self.assertEqual(StatusChangeLog.objects.get().user.id, user.id)
        self.assertEqual(StatusChangeLog.objects.get().record.id, record.id)
        self.assertEqual(StatusChangeLog.objects.get().time, time)

    def test_list_status_change_log(self):
        '''StatusChangeLog list should be accessed by GET request.'''
        url = reverse('statuschangelog-list')

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_delete_status_change_log(self):
        '''StatusChangeLog should be deleted by DELETE request.'''
        campus_event = mommy.make(training_event.models.CampusEvent)
        record = mommy.make(training_record.models.Record,
                            campus_event=campus_event)
        log = mommy.make(training_record.models.StatusChangeLog,
                         record=record)
        url = reverse('statuschangelog-detail', args=(log.pk,))

        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(StatusChangeLog.objects.count(), 0)

    def test_get_status_change_log(self):
        '''StatusChangeLog should be accessed by GET request.'''
        campus_event = mommy.make(training_event.models.CampusEvent)
        record = mommy.make(training_record.models.Record,
                            campus_event=campus_event)
        log = mommy.make(training_record.models.StatusChangeLog,
                         record=record)
        url = reverse('statuschangelog-detail', args=(log.pk,))
        expected_keys = {'id', 'record', 'time', 'user', 'pre_status',
                         'post_status'}

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(set(response.data.keys()), expected_keys)

    def test_update_status_change_log(self):
        '''StatusChangeLog should be updated by PATCH request.'''
        pre_status0 = Record.STATUS_SUBMITTED
        pre_status1 = Record.STATUS_FACULTY_ADMIN_REVIEWED
        campus_event = mommy.make(training_event.models.CampusEvent)
        record = mommy.make(training_record.models.Record,
                            campus_event=campus_event)
        log = mommy.make(training_record.models.StatusChangeLog,
                         record=record, pre_status=pre_status0)
        url = reverse('statuschangelog-detail', args=(log.pk,))
        data = {'pre_status': pre_status1}

        response = self.client.patch(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('pre_status', response.data)
        self.assertEqual(response.data['pre_status'], pre_status1)
