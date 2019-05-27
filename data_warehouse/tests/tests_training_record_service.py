'''Unit tests for training record service.'''
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from model_mommy import mommy
from data_warehouse.services.training_record_service import (
    TrainingRecordService)
from auth.models import Department
from auth.services import PermissionService
from auth.utils import assign_perm
from training_record.models import Record
import training_event.models

User = get_user_model()


class TestTableExportServices(APITestCase):
    '''Unit tests for training record service.'''
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

    def test_get_records(self):
        '''Should return matched records.'''
        for _ in range(10):
            off_campus_event = mommy.make(training_event.models.OffCampusEvent)
            record = mommy.make(
                Record,
                user=self.user,
                off_campus_event=off_campus_event,)
            PermissionService.assign_object_permissions(self.user, record)
        records = TrainingRecordService.get_records(
            self.user, '', '', '2000-01-01', '2020-02-02')
        self.assertEqual(len(records), 10)
