'''Unit tests for training_record views.'''
from django.contrib.auth import get_user_model
from django.urls import reverse
from model_mommy import mommy
from rest_framework import status
from rest_framework.test import APITestCase

import training_record.models
from training_event.models import CampusEvent, OffCampusEvent


User = get_user_model()


class TestRecordViewSet(APITestCase):
    '''Unit tests for Record view.'''
    def test_create_record(self):
        '''Record should be created by POST request.'''
        url = reverse('record-list')
        campus_event = mommy.make(training_event.models.CampusEvent)
        off_campus_event = mommy.make(training_event.models.OffCampusEvent)
        user = mommy.make(User)
        status = STATUS_SUBMITTED
        data = {'user':user.id,'campus_event':campus_event,
                'off_campus_event':off_campus_event,'status':status}

        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(training_record.models.Record.objects.count(), 1)
        self.assertEqual(training_record.models.Record.objects.get().user.id,user.id)
        self.assertEqual(training_record.models.Record.objects.get().campus_event,campus_event)
        self.assertEqual(training_record.models.Record.objects.get().off_campus_event,off_campus_event)
        self.assertEqual(training_record.models.Record.objects.get().status,status)

    def test_list_record(self):
        '''Record list should be accessed by GET request.'''
        url = reverse('record-list')

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_delete_record(self):
        '''Record should be deleted by DELETE request.'''
        record = mommy.make(training_record.models.Record)
        url = reverse('record-detail', args=(record.pk,))

        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(training_record.models.Record.objects.count(), 0)

    def test_get_record(self):
        '''Record should be accessed by GET request.'''
        record = mommy.make(training_record.models.Record)
        url = reverse('record-detail', args=(record.pk,))
        expected_keys = {'id', 'create_time', 'update_time', 'campus_event ', 
                        'off_campus_event','user','status'}

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(set(response.data.keys()), expected_keys)

    def test_update_record(self):
        '''Record should be updated by PATCH request.'''
        status0 = STATUS_SUBMITTED
        status1 = STATUS_FACULTY_ADMIN_REVIEWED
        record = mommy.make(training_record.models.Record, status=status0)
        url = reverse('record-detail', args=(record.pk,))
        data = {'status': status1}

        response = self.client.patch(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('status', response.data)
        self.assertEqual(response.data['status'], status1)


class TestRecordContentViewSet(APITestCase):
    '''Unit tests for RecordContent view.'''
    def test_create_recordcontent(self):
        '''RecordContent should be created by POST request.'''
        url = reverse('recordcontent-list')
        
        record = mommy.make(training_record.models.Record)
        content_type = CONTENT_TYPE_CONTENT
        content = "ABC"
        data = {'record':record,'content_type':content_type,'content':content}

        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(training_record.models.RecordContent.objects.count(), 1)
        self.assertEqual(training_record.models.RecordContent.objects.get().record, record)
        self.assertEqual(training_record.models.RecordContent.objects.get().content_type, content_type)
        self.assertEqual(training_record.models.RecordContent.objects.get().content, content)

        
    def test_list_recordcontent(self):
        '''RecordContent list should be accessed by GET request.'''
        url = reverse('recordcontent-list')

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_delete_recordcontent(self):
        '''RecordContent should be deleted by DELETE request.'''
        recordcontent = mommy.make(training_record.models.RecordContent)
        url = reverse('recordcontent-detail', args=(recordcontent.pk,))

        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(training_record.models.RecordContent.objects.count(), 0)

    def test_get_recordcontent(self):
        '''RecordContent should be accessed by GET request.'''
        recordcontent = mommy.make(training_record.models.RecordContent)
        url = reverse('recordcontent-detail', args=(recordcontent.pk,))
        expected_keys = {'id', 'create_time', 'update_time', 'record', 
                        'content_type','content'}

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(set(response.data.keys()), expected_keys)

    def test_update_recordcontent(self):
        '''RecordContent should be updated by PATCH request.'''
        content_type0 = CONTENT_TYPE_CONTENT
        content_type1 = CONTENT_TYPE_SUMMARY
        recordcontent = mommy.make(training_record.models.RecordContent, content_type=content_type0)
        url = reverse('recordcontent-detail', args=(recordcontent.pk,))
        data = {'content_type': content_type1}

        response = self.client.patch(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('content_type', response.data)
        self.assertEqual(response.data['content_type'], content_type1)


class TestRecordAttachmentViewSet(APITestCase):
    '''Unit tests for RecordAttachment view.'''
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
        '''RecordAttachment list should be accessed by GET request.'''
        url = reverse('recordattachment-list')

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_delete_recordattachment(self):
        '''RecordAttachment should be deleted by DELETE request.'''
        recordattachment = mommy.make(training_record.models.RecordAttachment)
        url = reverse('recordattachment-detail', args=(recordattachment.pk,))

        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(training_record.models.RecordAttachment.objects.count(), 0)

    def test_get_recordattachment(self):
        '''RecordAttachment should be accessed by GET request.'''
        recordattachment = mommy.make(training_record.models.RecordAttachment)
        url = reverse('recordattachment-detail', args=(recordattachment.pk,))
        expected_keys = {'id', 'create_time', 'update_time', 'record', 
                        'attachment_type','path'}

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(set(response.data.keys()), expected_keys)

    def test_update_recordattachment(self):
        '''RecordAttachment should be updated by PATCH request.'''
        attachment_type0 = ATTACHMENT_TYPE_CONTENT
        attachment_type1 = ATTACHMENT_TYPE_SUMMARY
        recordattachment = mommy.make(training_record.models.RecordAttachment, attachment_type=attachment_type0)
        url = reverse('recordattachment-detail', args=(recordattachment.pk,))
        data = {'attachment_type': attachment_type1}

        response = self.client.patch(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('attachment_type', response.data)
        self.assertEqual(response.data['attachment_type'], attachment_type1)


class TestStatusChangeLogViewSet(APITestCase):
    '''Unit tests for StatusChangeLog view.'''
    def test_create_statuschangelog(self):
        '''StatusChangeLog should be created by POST request.'''
        url = reverse('statuschangelog-list')

        record = mommy.make(training_record.models.Record)
        pre_status = Record.STATUS_SUBMITTED
        post_status = Record.STATUS_FACULTY_ADMIN_REVIEWED
        user = mommy.make(User)
        data = {'user': user, 'pre_status':pre_status, 'post_status':post_status, 'record':record}

        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(training_record.models.StatusChangeLog.objects.count(), 1)
        self.assertEqual(training_record.models.StatusChangeLog.objects.get().user, user)
        self.assertEqual(training_record.models.StatusChangeLog.objects.get().pre_status, pre_status)
        self.assertEqual(training_record.models.StatusChangeLog.objects.get().post_status, post_status)
        self.assertEqual(training_record.models.StatusChangeLog.objects.get().record, record)

    def test_list_statuschangelog(self):
        '''StatusChangeLog list should be accessed by GET request.'''
        url = reverse('statuschangelog-list')

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_delete_statuschangelog(self):
        '''StatusChangeLog should be deleted by DELETE request.'''
        statuschangelog = mommy.make(training_record.models.StatusChangeLog)
        url = reverse('statuschangelog-detail', args=(statuschangelog.pk,))

        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(training_record.models.StatusChangeLog.objects.count(), 0)

    def test_get_statuschangelog(self):
        '''StatusChangeLog should be accessed by GET request.'''
        statuschangelog = mommy.make(training_record.models.StatusChangeLog)
        url = reverse('statuschangelog-detail', args=(statuschangelog.pk,))
        expected_keys = {'id', 'record', 'pre_status', 'post_status', 'time', 'user'}

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(set(response.data.keys()), expected_keys)

    def test_update_statuschangelog(self):
        '''StatusChangeLog should be updated by PATCH request.'''
        pre_status0 = Record.STATUS_SUBMITTED
        pre_status1 = Record.STATUS_FACULTY_ADMIN_REVIEWED
        statuschangelog = mommy.make(training_record.models.StatusChangeLog, pre_status=pre_status0)
        url = reverse('statuschangelog-detail', args=(statuschangelog.pk,))
        data = {'pre_status': pre_status1}

        response = self.client.patch(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('pre_status', response.data)
        self.assertEqual(response.data['pre_status'], pre_status1)