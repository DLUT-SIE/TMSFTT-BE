'''Unit tests for training_record views.'''
import io
from django.contrib.auth import get_user_model
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
    def test_create_record(self):
        '''Record should be created by POST request.'''

        campus_event = mommy.make(training_event.models.CampusEvent)
        user = mommy.make(User)
        url = reverse('record-list')
        data = {'campus_event': campus_event.id, 'user': user.id}

        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(training_record.models.Record.objects.count(), 1)
<<<<<<< HEAD
        self.assertEqual(
            training_record.models.Record.objects.get().campus_event.id,
            campus_event.id)
        self.assertEqual(
            training_record.models.Record.objects.get().user.id, user.id)
=======
        self.assertEqual(training_record.models.Record.objects.get().user.id,user.id)
        self.assertEqual(training_record.models.Record.objects.get().campus_event,campus_event)
        self.assertEqual(training_record.models.Record.objects.get().off_campus_event,off_campus_event)
        self.assertEqual(training_record.models.Record.objects.get().status,status)
>>>>>>> yuanqing zancun

    def test_list_record(self):
        '''Record list should be accessed by GET request.'''
        url = reverse('record-list')

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_delete_record(self):
        '''Record should be deleted by DELETE request.'''
<<<<<<< HEAD
        campus_event = mommy.make(training_event.models.CampusEvent)
        record = mommy.make(training_record.models.Record,
                            campus_event=campus_event)
=======
        record = mommy.make(training_record.models.Record)
>>>>>>> yuanqing zancun
        url = reverse('record-detail', args=(record.pk,))

        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(training_record.models.Record.objects.count(), 0)

    def test_get_record(self):
        '''Record should be accessed by GET request.'''
<<<<<<< HEAD
        campus_event = mommy.make(training_event.models.CampusEvent)
        record = mommy.make(training_record.models.Record,
                            campus_event=campus_event)
        url = reverse('record-detail', args=(record.pk,))
        expected_keys = {'id', 'create_time', 'update_time', 'campus_event',
                         'off_campus_event', 'user', 'status'}
=======
        record = mommy.make(training_record.models.Record)
        url = reverse('record-detail', args=(record.pk,))
        expected_keys = {'id', 'create_time', 'update_time', 'campus_event ', 
                        'off_campus_event','user','status'}
>>>>>>> yuanqing zancun

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(set(response.data.keys()), expected_keys)

    def test_update_record(self):
        '''Record should be updated by PATCH request.'''
<<<<<<< HEAD
        status0 = training_record.models.Record.STATUS_SUBMITTED
        status1 = training_record.models.Record.STATUS_FACULTY_ADMIN_REVIEWED
        campus_event = mommy.make(training_event.models.CampusEvent)
        record = mommy.make(training_record.models.Record,
                            campus_event=campus_event, status=status0)
=======
        status0 = STATUS_SUBMITTED
        status1 = STATUS_FACULTY_ADMIN_REVIEWED
        record = mommy.make(training_record.models.Record, status=status0)
>>>>>>> yuanqing zancun
        url = reverse('record-detail', args=(record.pk,))
        data = {'status': status1}

        response = self.client.patch(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('status', response.data)
        self.assertEqual(response.data['status'], status1)


class TestRecordContentViewSet(APITestCase):
    '''Unit tests for RecordContent view.'''
<<<<<<< HEAD
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
=======
    def test_create_recordcontent(self):
        '''RecordContent should be created by POST request.'''
        url = reverse('recordcontent-list')
        
        record = mommy.make(training_record.models.Record)
        content_type = CONTENT_TYPE_CONTENT
        content = "ABC"
        data = {'record':record,'content_type':content_type,'content':content}
>>>>>>> yuanqing zancun

        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
<<<<<<< HEAD
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
=======
        self.assertEqual(training_record.models.RecordContent.objects.count(), 1)
        self.assertEqual(training_record.models.RecordContent.objects.get().record, record)
        self.assertEqual(training_record.models.RecordContent.objects.get().content_type, content_type)
        self.assertEqual(training_record.models.RecordContent.objects.get().content, content)

        
    def test_list_recordcontent(self):
>>>>>>> yuanqing zancun
        '''RecordContent list should be accessed by GET request.'''
        url = reverse('recordcontent-list')

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

<<<<<<< HEAD
    def test_delete_record_content(self):
        '''RecordContent should be deleted by DELETE request.'''
        campus_event = mommy.make(training_event.models.CampusEvent)
        record = mommy.make(training_record.models.Record,
                            campus_event=campus_event)
        record_content = mommy.make(training_record.models.RecordContent,
                                    record=record)
        url = reverse('recordcontent-detail', args=(record_content.pk,))
=======
    def test_delete_recordcontent(self):
        '''RecordContent should be deleted by DELETE request.'''
        recordcontent = mommy.make(training_record.models.RecordContent)
        url = reverse('recordcontent-detail', args=(recordcontent.pk,))
>>>>>>> yuanqing zancun

        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
<<<<<<< HEAD
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
=======
        self.assertEqual(training_record.models.RecordContent.objects.count(), 0)

    def test_get_recordcontent(self):
        '''RecordContent should be accessed by GET request.'''
        recordcontent = mommy.make(training_record.models.RecordContent)
        url = reverse('recordcontent-detail', args=(recordcontent.pk,))
        expected_keys = {'id', 'create_time', 'update_time', 'record', 
                        'content_type','content'}
>>>>>>> yuanqing zancun

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(set(response.data.keys()), expected_keys)

<<<<<<< HEAD
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
=======
    def test_update_recordcontent(self):
        '''RecordContent should be updated by PATCH request.'''
        content_type0 = CONTENT_TYPE_CONTENT
        content_type1 = CONTENT_TYPE_SUMMARY
        recordcontent = mommy.make(training_record.models.RecordContent, content_type=content_type0)
        url = reverse('recordcontent-detail', args=(recordcontent.pk,))
>>>>>>> yuanqing zancun
        data = {'content_type': content_type1}

        response = self.client.patch(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('content_type', response.data)
        self.assertEqual(response.data['content_type'], content_type1)


class TestRecordAttachmentViewSet(APITestCase):
    '''Unit tests for RecordAttachment view.'''
<<<<<<< HEAD
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
=======
    def test_create_recordattachment(self):
        '''RecordAttachment should be created by POST request.'''
        url = reverse('recordattachment-list')

        record = mommy.make(training_record.models.Record)
        attachment_type = ATTACHMENT_TYPE_CONTENT
        path = ''
        data = {'record': record,'attachment_type':attachment_type,'path':path}

        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(training_record.models.RecordAttachment.objects.count(), 1)
        self.assertEqual(training_record.models.RecordAttachment.objects.get().record, record)
        self.assertEqual(training_record.models.RecordAttachment.objects.get().attachment_type, attachment_type)
        self.assertEqual(training_record.models.RecordAttachment.objects.get().path, path)

    def test_list_recordattachment(self):
>>>>>>> yuanqing zancun
        '''RecordAttachment list should be accessed by GET request.'''
        url = reverse('recordattachment-list')

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

<<<<<<< HEAD
    def test_delete_record_attachment(self):
        '''RecordAttachment should be deleted by DELETE request.'''
        campus_event = mommy.make(training_event.models.CampusEvent)
        record = mommy.make(training_record.models.Record,
                            campus_event=campus_event)
        record_attachment = mommy.make(training_record.models.RecordAttachment,
                                       record=record)
        url = reverse('recordattachment-detail', args=(record_attachment.pk,))
=======
    def test_delete_recordattachment(self):
        '''RecordAttachment should be deleted by DELETE request.'''
        recordattachment = mommy.make(training_record.models.RecordAttachment)
        url = reverse('recordattachment-detail', args=(recordattachment.pk,))
>>>>>>> yuanqing zancun

        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
<<<<<<< HEAD
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
=======
        self.assertEqual(training_record.models.RecordAttachment.objects.count(), 0)

    def test_get_recordattachment(self):
        '''RecordAttachment should be accessed by GET request.'''
        recordattachment = mommy.make(training_record.models.RecordAttachment)
        url = reverse('recordattachment-detail', args=(recordattachment.pk,))
        expected_keys = {'id', 'create_time', 'update_time', 'record', 
                        'attachment_type','path'}
>>>>>>> yuanqing zancun

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(set(response.data.keys()), expected_keys)

<<<<<<< HEAD
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
=======
    def test_update_recordattachment(self):
        '''RecordAttachment should be updated by PATCH request.'''
        attachment_type0 = ATTACHMENT_TYPE_CONTENT
        attachment_type1 = ATTACHMENT_TYPE_SUMMARY
        recordattachment = mommy.make(training_record.models.RecordAttachment, attachment_type=attachment_type0)
        url = reverse('recordattachment-detail', args=(recordattachment.pk,))
>>>>>>> yuanqing zancun
        data = {'attachment_type': attachment_type1}

        response = self.client.patch(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('attachment_type', response.data)
        self.assertEqual(response.data['attachment_type'], attachment_type1)


class TestStatusChangeLogViewSet(APITestCase):
    '''Unit tests for StatusChangeLog view.'''
<<<<<<< HEAD
    def test_create_status_change_log(self):
        '''StatusChangeLog should be created by POST request.'''
        url = reverse('statuschangelog-list')

        campus_event = mommy.make(training_event.models.CampusEvent)
        record = mommy.make(training_record.models.Record,
                            campus_event=campus_event)
        user = mommy.make(User)
        time = now()
        data = {'user': user.id, 'time': time, 'record': record.id}
=======
    def test_create_statuschangelog(self):
        '''StatusChangeLog should be created by POST request.'''
        url = reverse('statuschangelog-list')

        record = mommy.make(training_record.models.Record)
        pre_status = Record.STATUS_SUBMITTED
        post_status = Record.STATUS_FACULTY_ADMIN_REVIEWED
        user = mommy.make(User)
        data = {'user': user, 'pre_status':pre_status, 'post_status':post_status, 'record':record}
>>>>>>> yuanqing zancun

        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
<<<<<<< HEAD
        self.assertEqual(StatusChangeLog.objects.count(), 1)
        self.assertEqual(StatusChangeLog.objects.get().user.id, user.id)
        self.assertEqual(StatusChangeLog.objects.get().record.id, record.id)
        self.assertEqual(StatusChangeLog.objects.get().time, time)

    def test_list_status_change_log(self):
=======
        self.assertEqual(training_record.models.StatusChangeLog.objects.count(), 1)
        self.assertEqual(training_record.models.StatusChangeLog.objects.get().user, user)
        self.assertEqual(training_record.models.StatusChangeLog.objects.get().pre_status, pre_status)
        self.assertEqual(training_record.models.StatusChangeLog.objects.get().post_status, post_status)
        self.assertEqual(training_record.models.StatusChangeLog.objects.get().record, record)

    def test_list_statuschangelog(self):
>>>>>>> yuanqing zancun
        '''StatusChangeLog list should be accessed by GET request.'''
        url = reverse('statuschangelog-list')

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

<<<<<<< HEAD
    def test_delete_status_change_log(self):
        '''StatusChangeLog should be deleted by DELETE request.'''
        campus_event = mommy.make(training_event.models.CampusEvent)
        record = mommy.make(training_record.models.Record,
                            campus_event=campus_event)
        log = mommy.make(training_record.models.StatusChangeLog,
                         record=record)
        url = reverse('statuschangelog-detail', args=(log.pk,))
=======
    def test_delete_statuschangelog(self):
        '''StatusChangeLog should be deleted by DELETE request.'''
        statuschangelog = mommy.make(training_record.models.StatusChangeLog)
        url = reverse('statuschangelog-detail', args=(statuschangelog.pk,))
>>>>>>> yuanqing zancun

        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
<<<<<<< HEAD
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
=======
        self.assertEqual(training_record.models.StatusChangeLog.objects.count(), 0)

    def test_get_statuschangelog(self):
        '''StatusChangeLog should be accessed by GET request.'''
        statuschangelog = mommy.make(training_record.models.StatusChangeLog)
        url = reverse('statuschangelog-detail', args=(statuschangelog.pk,))
        expected_keys = {'id', 'record', 'pre_status', 'post_status', 'time', 'user'}
>>>>>>> yuanqing zancun

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(set(response.data.keys()), expected_keys)

<<<<<<< HEAD
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
=======
    def test_update_statuschangelog(self):
        '''StatusChangeLog should be updated by PATCH request.'''
        pre_status0 = Record.STATUS_SUBMITTED
        pre_status1 = Record.STATUS_FACULTY_ADMIN_REVIEWED
        statuschangelog = mommy.make(training_record.models.StatusChangeLog, pre_status=pre_status0)
        url = reverse('statuschangelog-detail', args=(statuschangelog.pk,))
>>>>>>> yuanqing zancun
        data = {'pre_status': pre_status1}

        response = self.client.patch(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('pre_status', response.data)
<<<<<<< HEAD
        self.assertEqual(response.data['pre_status'], pre_status1)
=======
        self.assertEqual(response.data['pre_status'], pre_status1)
>>>>>>> yuanqing zancun
