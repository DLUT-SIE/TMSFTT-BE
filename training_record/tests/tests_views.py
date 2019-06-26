'''Unit tests for training_record views.'''
import io
import tempfile
import json
from unittest.mock import patch, PropertyMock

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.test import override_settings
from django.urls import reverse
from model_mommy import mommy
from rest_framework import status
from rest_framework.test import APITestCase

from auth.utils import assign_perm
from auth.services import PermissionService
from auth.models import Department
import training_record.models
from training_record.models import (
    Record, RecordContent, CampusEventFeedback)
import training_event.models
from training_event.models import EventCoefficient

User = get_user_model()


class TestRecordViewSet(APITestCase):
    '''Unit tests for Record view.'''
    @classmethod
    def setUpTestData(cls):
        depart = mommy.make(Department, name="创新创业学院")
        cls.user = mommy.make(User, department=depart)
        cls.group = mommy.make(Group, name="个人权限")
        cls.user.groups.add(cls.group)
        assign_perm('training_record.add_record', cls.group)
        assign_perm('training_record.view_record', cls.group)
        assign_perm('training_record.change_record', cls.group)

    def setUp(self):
        self.client.force_authenticate(self.user)

    @patch('os.path.splitext', lambda x: ('a', '.png'))
    def test_create_record(self):
        '''Record should be created by POST request.'''
        user = mommy.make(User)
        url = reverse('record-list')
        off_campus_event = {
            'name': 'abc',
            'time': '0122-12-31T15:54:17.000Z',
            'location': 'loc',
            'num_hours': 5,
            'num_participants': 30,
        }
        attachments = [io.BytesIO(b'some content') for _ in range(3)]
        contents = [
            json.dumps({'content_type': x[0], 'content': 'abc'})
            for x in RecordContent.CONTENT_TYPE_CHOICES]
        data = {
            'off_campus_event': json.dumps(off_campus_event),
            'user': user.id,
            'contents': contents,
            'attachments': attachments,
            'role': EventCoefficient.ROLE_PARTICIPATOR,
        }

        response = self.client.post(url, data, format='multipart')
        event = training_event.models.OffCampusEvent.objects.get()

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(training_record.models.Record.objects.count(), 1)
        self.assertEqual(
            training_record.models.Record.objects.get().off_campus_event.id,
            event.id)
        self.assertEqual(
            training_record.models.Record.objects.get().user.id, self.user.id)

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
            record = mommy.make(
                Record,
                user=self.user,
                off_campus_event=off_campus_event,
                status=Record.STATUS_SCHOOL_ADMIN_APPROVED
                if index % 4 == 0 else Record.STATUS_SUBMITTED)
            PermissionService.assign_object_permissions(self.user, record)

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

    def test_list_records_for_review(self):
        '''should return records for admin'''
        url = reverse('record-list-records-for-review')
        for _ in range(10):
            off_campus_event = mommy.make(training_event.models.OffCampusEvent)
            record = mommy.make(
                Record,
                user=self.user,
                off_campus_event=off_campus_event,
                status=Record.STATUS_DEPARTMENT_ADMIN_APPROVED,
                )
            PermissionService.assign_object_permissions(self.user, record)

        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 10)

    def test_search_record_with_no_query_params(self):
        '''should return matched records'''
        url = reverse('record-list') + '?start_time=2013-09-09&'\
            'end_time=2014-08-08&event_name=a&event_location=a'
        for _ in range(10):
            off_campus_event = mommy.make(training_event.models.OffCampusEvent)
            record = mommy.make(Record,
                                user=self.user,
                                off_campus_event=off_campus_event,)
            PermissionService.assign_object_permissions(self.user, record)

        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 0)

    def test_get_record(self):
        '''Record should be accessed by GET request.'''
        campus_event = mommy.make(training_event.models.CampusEvent)
        record = mommy.make(training_record.models.Record,
                            user=self.user,
                            campus_event=campus_event)
        url = reverse('record-detail', args=(record.pk,))
        expected_keys = {'id', 'create_time', 'update_time', 'campus_event',
                         'off_campus_event', 'user', 'status', 'contents',
                         'attachments', 'status_str', 'role', 'role_str',
                         'feedback', 'allow_actions_from_user',
                         'allow_actions_from_admin'}
        PermissionService.assign_object_permissions(self.user, record)
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(set(response.data.keys()), expected_keys)

    @patch('training_record.utils.is_user_allowed_operating')
    def test_update_record(self, mocked_method):
        '''Record should be updated by PATCH request.'''
        off_campus_event = mommy.make(training_event.models.OffCampusEvent,
                                      id=1,)
        off_campus_event_data = {
            'id': 1,
            'name': 'abc',
            'time': '0122-12-31T15:54:17.000Z',
            'location': 'loc',
            'num_hours': 5,
            'num_participants': 30,
        }
        type(self.user).is_teacher = PropertyMock(return_value=True)
        mocked_method.return_value(True)
        record = mommy.make(training_record.models.Record,
                            user=self.user,
                            off_campus_event=off_campus_event)
        PermissionService.assign_object_permissions(self.user, record)
        url = reverse('record-detail', args=(record.pk,))
        data = {'off_campus_event': json.dumps(off_campus_event_data),
                'contents': [],
                'attachments': [],
                'role': EventCoefficient.ROLE_PARTICIPATOR,
                'user': self.user.id}

        response = self.client.patch(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    @patch('training_record.services.NotificationService'
           '.send_system_notification')
    def test_department_admin_review(self, _):
        '''Should call department_admin_review.'''
        off_campus_event = mommy.make(training_event.models.OffCampusEvent)
        record = mommy.make(training_record.models.Record,
                            off_campus_event=off_campus_event,
                            status=Record.STATUS_SUBMITTED)
        user = mommy.make(User)
        group = mommy.make(Group, name="创新创业学院-管理员")
        user.groups.add(group)
        assign_perm('training_record.review_record', group)
        PermissionService.assign_object_permissions(self.user, record)

        url = reverse('record-department-admin-review', args=(record.pk,))

        self.client.force_authenticate(user)
        data = {'isApproved': True}
        response = self.client.post(url, data)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    @patch('training_record.services.NotificationService'
           '.send_system_notification')
    def test_school_admin_review(self, _):
        '''Should call department_admin_review.'''
        off_campus_event = mommy.make(training_event.models.OffCampusEvent)
        record = mommy.make(training_record.models.Record,
                            off_campus_event=off_campus_event,
                            status=Record.STATUS_DEPARTMENT_ADMIN_APPROVED)
        user = mommy.make(User)
        group = mommy.make(Group, name="创新创业学院-管理员")
        user.groups.add(group)
        assign_perm('training_record.review_record', group)
        PermissionService.assign_object_permissions(self.user, record)

        url = reverse('record-school-admin-review', args=(record.pk,))

        self.client.force_authenticate(user)
        data = {'isApproved': True}
        response = self.client.post(url, data)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    @patch('training_record.services.NotificationService'
           '.send_system_notification')
    def test_close_record(self, _):
        '''Should call close_record.'''
        off_campus_event = mommy.make(training_event.models.OffCampusEvent)
        record = mommy.make(training_record.models.Record,
                            off_campus_event=off_campus_event,
                            status=Record.STATUS_DEPARTMENT_ADMIN_APPROVED)
        user = mommy.make(User)
        group = mommy.make(Group, name="创新创业学院-管理员")
        user.groups.add(group)
        assign_perm('training_record.change_record', group)
        PermissionService.assign_object_permissions(self.user, record)

        url = reverse('record-close-record', args=(record.pk,))

        self.client.force_authenticate(user)
        response = self.client.post(url)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    @patch('training_record.services.NotificationService'
           '.send_system_notification')
    def test_force_close_record(self, _):
        '''Should force close campus record.'''
        campus_event = mommy.make(training_event.models.CampusEvent)
        user = mommy.make(User)
        record = mommy.make(training_record.models.Record,
                            campus_event=campus_event,
                            user=user,
                            status=Record.STATUS_FEEDBACK_SUBMITTED)
        group = mommy.make(Group, name="创新创业学院-管理员")
        user.groups.add(group)
        type(user).is_school_admin = PropertyMock(return_value=True)
        assign_perm('training_record.change_record', group)
        PermissionService.assign_object_permissions(self.user, record)

        data = {
            'campus_event': campus_event.id,
            'user_id': user.id,
        }

        url = reverse('record-force-close-record')

        self.client.force_authenticate(user)

        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    @patch('training_record.views.RecordService')
    def test_batch_submit(self, mocked_service):
        '''Should batch create records according to request.'''
        user = mommy.make(get_user_model())
        group = mommy.make(Group, name="创新创业学院-管理员")
        user.groups.add(group)
        assign_perm('training_record.batchadd_record', group)
        url = reverse('record-batch-submit')
        file_data = io.BytesIO(b'some numbers')
        mocked_service.create_campus_records_from_excel.return_value = 3

        self.client.force_authenticate(user)
        response = self.client.post(url, {'file': file_data})

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('count', response.data)

    @patch('training_record.views.RecordService')
    def test_get_number_of_records_without_feedback(self, mocked_service):
        '''Should return the count of records which requiring feedback'''
        user = mommy.make(get_user_model())
        group = mommy.make(Group, name="创新创业学院-管理员")
        user.groups.add(group)
        assign_perm('training_record.view_record', group)
        url = reverse('record-get-number-of-records-without-feedback')
        mocked_service.get_number_of_records_without_feedback.return_value = 2

        self.client.force_authenticate(user)
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('count', response.data)


class TestRecordContentViewSet(APITestCase):
    '''Unit tests for RecordContent view.'''
    @classmethod
    def setUpTestData(cls):
        cls.user = mommy.make(User)
        cls.group = mommy.make(Group, name="个人权限")
        cls.user.groups.add(cls.group)
        assign_perm('training_record.view_recordcontent', cls.group)

    def setUp(self):
        self.client.force_authenticate(self.user)

    def test_list_record_content(self):
        '''RecordContent list should be accessed by GET request.'''
        url = reverse('recordcontent-list')

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)


@override_settings(MEDIA_ROOT=tempfile.gettempdir())
class TestRecordAttachmentViewSet(APITestCase):
    '''Unit tests for RecordAttachment view.'''
    @classmethod
    def setUpTestData(cls):
        cls.user = mommy.make(User)
        cls.group = mommy.make(Group, name="个人权限")
        cls.user.groups.add(cls.group)
        assign_perm('training_record.view_recordattachment', cls.group)

    def setUp(self):
        self.client.force_authenticate(self.user)

    def test_list_record_attachment(self):
        '''RecordAttachment list should be accessed by GET request.'''
        url = reverse('recordattachment-list')

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)


class TestStatusChangeLogViewSet(APITestCase):
    '''Unit tests for StatusChangeLog view.'''
    @classmethod
    def setUpTestData(cls):
        cls.user = mommy.make(User)

    def setUp(self):
        self.client.force_authenticate(self.user)

    def test_list_status_change_log(self):
        '''StatusChangeLog list should be accessed by GET request.'''
        url = reverse('statuschangelog-list')

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_status_change_log(self):
        '''StatusChangeLog should be accessed by GET request.'''
        campus_event = mommy.make(training_event.models.CampusEvent)
        record = mommy.make(training_record.models.Record,
                            campus_event=campus_event)
        log = mommy.make(training_record.models.StatusChangeLog,
                         record=record)
        url = reverse('statuschangelog-detail', args=(log.pk,))
        expected_keys = {'id', 'record', 'time', 'user', 'pre_status',
                         'post_status', 'post_status_str', 'pre_status_str'}

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(set(response.data.keys()), expected_keys)


class TestCampusEventFeedbackViewSet(APITestCase):
    '''Unit tests for CampusEventFeedback view.'''
    @classmethod
    def setUpTestData(cls):
        cls.user = mommy.make(User)
        cls.group = mommy.make(Group, name="个人权限")
        cls.user.groups.add(cls.group)
        assign_perm('training_record.add_campuseventfeedback', cls.group)

    def setUp(self):
        self.client.force_authenticate(self.user)

    def test_create_campus_event_feedback(self):
        '''CampusEventFeedback should be created by POST request.'''
        url = reverse('campuseventfeedback-list')
        campus_event = mommy.make(
            training_event.models.CampusEvent, name='1243')
        record = mommy.make(
            Record,
            campus_event=campus_event,
            status=Record.STATUS_SCHOOL_ADMIN_APPROVED)
        data = {
            'record': record.id,
            'content': '1',
        }
        assign_perm('training_record.change_record', self.user, record)
        PermissionService.assign_object_permissions(self.user, record)
        response = self.client.post(url, data, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(CampusEventFeedback.objects.count(), 1)
