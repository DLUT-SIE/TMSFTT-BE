'''Unit tests for training_record services.'''
import io
import tempfile
from unittest.mock import Mock
import xlwt

from django.test import TestCase
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.core.files.uploadedfile import InMemoryUploadedFile
from model_mommy import mommy

from auth.utils import assign_perm
from infra.exceptions import BadRequest
from training_record.models import (
    RecordContent, RecordAttachment, CampusEventFeedback, Record)
from training_record.services import RecordService, CampusEventFeedbackService
from training_event.models import CampusEvent, OffCampusEvent, EventCoefficient


User = get_user_model()


# pylint: disable=too-many-public-methods
class TestRecordService(TestCase):
    '''Test services provided by RecordService.'''
    @classmethod
    def setUpTestData(cls):
        cls.off_campus_event = {
            'name': 'abc',
            'time': '0122-12-31T15:54:17.000Z',
            'location': 'loc',
            'num_hours': 5,
            'num_participants': 30,
        }
        cls.attachments = [
            InMemoryUploadedFile(
                io.BytesIO(b'some content'),
                'path', 'name', 'content_type', 'size', 'charset')
            for _ in range(3)]
        cls.contents = [
            {'content_type': x[0], 'content': 'abc'}
            for x in RecordContent.CONTENT_TYPE_CHOICES]

        cls.campus_event = mommy.make(CampusEvent)
        cls.user = mommy.make(User)
        cls.group = mommy.make(Group, name="个人权限")
        cls.user.groups.add(cls.group)
        cls.event_coefficient = mommy.make(EventCoefficient)
        cls.off_campus_event_instance = mommy.make(OffCampusEvent)
        cls.off_campus_event_data = {
            'id': cls.off_campus_event_instance.id,
            'name': cls.off_campus_event_instance.name,
            'time': cls.off_campus_event_instance.time,
            'location': cls.off_campus_event_instance.location,
            'num_hours': cls.off_campus_event_instance.num_hours,
            'num_participants': cls.off_campus_event_instance.num_participants
        }
        cls.record = mommy.make(Record,
                                off_campus_event=cls.off_campus_event_instance,
                                user=cls.user)
        assign_perm('training_record.add_record', cls.group)
        assign_perm('training_record.view_record', cls.group)
        assign_perm('training_record.change_record', cls.group)

    def test_create_off_campus_record_no_event_data(self):
        '''Should raise ValueError if no off-campus event data.'''
        with self.assertRaisesMessage(
                BadRequest, '数据格式无效'):
            RecordService.create_off_campus_record_from_raw_data({})

    def test_create_off_campus_record_no_user(self):
        '''Should raise ValueError if no user.'''
        with self.assertRaisesMessage(
                BadRequest, '数据格式无效'):
            RecordService.create_off_campus_record_from_raw_data(
                {'off_campus_event': 1})

    def test_create_off_campus_records_no_role(self):
        '''Should raise ValueError if no role.'''
        user = mommy.make(User)

        data = {
            'off_campus_event': self.off_campus_event,
            'user': user,
            'contents': self.contents,
            'attachments': self.attachments,
        }
        with self.assertRaisesMessage(
                BadRequest, '数据格式无效'):
            RecordService.create_off_campus_record_from_raw_data(data)

    def test_create_off_campus_record(self):
        '''Should complete full creation.'''
        user = mommy.make(User)

        data = {
            'off_campus_event': self.off_campus_event,
            'user': user,
            'contents': self.contents,
            'attachments': self.attachments,
            'role': EventCoefficient.ROLE_EXPERT,
        }
        RecordService.create_off_campus_record_from_raw_data(data)

        self.assertEqual(
            RecordContent.objects.all().count(), len(self.contents),
        )
        self.assertEqual(
            RecordAttachment.objects.all().count(), len(self.attachments),
        )

    def test_update_off_campus_record_no_event_data(self):
        '''Should raise ValueError if no off-campus event data.'''
        with self.assertRaisesMessage(
                BadRequest, '数据格式无效'):
            RecordService.update_off_campus_record_from_raw_data(
                self.record, {}, {})

    def test_update_off_campus_record_too_much_attachments(self):
        '''BadRequest should be raised if attachments is too much'''
        user = mommy.make(User)
        attachments = [
            InMemoryUploadedFile(
                io.BytesIO(b'some content'),
                'path', 'name', 'content_type', 'size', 'charset')
            for _ in range(4)]
        request = Mock()
        request.user = user
        context = {
            'request': request,
        }
        data = {
            'off_campus_event': self.off_campus_event_data,
            'user': user,
            'contents': self.contents,
            'attachments': attachments,
            'role': EventCoefficient.ROLE_EXPERT,
        }
        with self.assertRaisesMessage(BadRequest, '最多允许上传3个附件'):
            RecordService.update_off_campus_record_from_raw_data(
                self.record, data, context
            )

    def test_update_off_campus_record_bad_record(self):
        '''Should raise ValueError if not found record.'''
        user = mommy.make(User)

        request = Mock()
        request.user = user
        context = {
            'request': request,
        }
        data = {
            'off_campus_event': self.off_campus_event_data,
            'user': user,
            'contents': self.contents,
            'attachments': self.attachments,
            'role': EventCoefficient.ROLE_EXPERT,
        }
        with self.assertRaisesMessage(BadRequest, '校外培训记录无效'):
            RecordService.update_off_campus_record_from_raw_data(
                self.off_campus_event_instance, data, context
            )

    def test_update_off_campus_records_no_role(self):
        '''Should raise ValueError if no role.'''
        user = mommy.make(User)

        request = Mock()
        request.user = user
        context = {
            'request': request,
        }
        data = {
            'off_campus_event': self.off_campus_event_data,
            'user': user,
            'contents': self.contents,
            'attachments': self.attachments,
        }
        with self.assertRaisesMessage(
                BadRequest, '数据格式无效'):
            RecordService.update_off_campus_record_from_raw_data(
                self.record, data, context)

    def test_update_off_campus_record(self):
        '''Should complete full creation.'''
        user = mommy.make(User)

        request = Mock()
        request.user = user
        context = {
            'request': request,
        }
        data = {
            'off_campus_event': self.off_campus_event_data,
            'user': user,
            'contents': self.contents,
            'attachments': self.attachments,
            'role': EventCoefficient.ROLE_EXPERT,
        }
        RecordService.update_off_campus_record_from_raw_data(
            self.record, data, context
        )

        self.assertEqual(
            RecordContent.objects.all().count(), len(self.contents),
        )
        self.assertEqual(
            RecordAttachment.objects.all().count(), len(self.attachments),
        )

    def test_create_campus_records_bad_file(self):
        '''Should raise Error if get invalid file.'''
        tup = tempfile.mkstemp()
        with self.assertRaisesMessage(
                BadRequest, '无效的表格'):
            RecordService.create_campus_records_from_excel(tup[0], '')

    def test_create_campus_records_bad_event_id(self):
        '''Should raise Error if get invalid event id.'''
        tup = tempfile.mkstemp()
        work_book = xlwt.Workbook()
        sheet = work_book.add_sheet(u'sheet1', cell_overwrite_ok=True)
        sheet.write(0, 1, self.campus_event.id+1)
        work_book.save(tup[1])
        with open(tup[0], 'rb') as work_book:
            excel = work_book.read()
        with self.assertRaisesMessage(
                BadRequest, '编号为{}的活动不存在'.format(self.campus_event.id+1)):
            RecordService.create_campus_records_from_excel(excel, '')

    def test_create_campus_records_bad_user_id(self):
        '''Should raise Error if get invalid user id.'''
        tup = tempfile.mkstemp()
        work_book = xlwt.Workbook()
        sheet = work_book.add_sheet(u'sheet1', cell_overwrite_ok=True)
        sheet.write(0, 1, self.campus_event.id)
        sheet.write(3, 2, self.user.id+1)
        sheet.write(3, 5, '6')
        work_book.save(tup[1])
        user = mommy.make(User)
        context = {
            'user': user,
        }
        assign_perm('training_event.change_campusevent',
                    user, self.campus_event)
        mommy.make(EventCoefficient,
                   campus_event=self.campus_event,
                   role=EventCoefficient.ROLE_PARTICIPATOR)
        mommy.make(EventCoefficient,
                   campus_event=self.campus_event,
                   role=EventCoefficient.ROLE_EXPERT)
        with open(tup[0], 'rb') as work_book:
            excel = work_book.read()
        with self.assertRaisesMessage(
                BadRequest,
                '第4行，编号为{}的用户不存在'.format(self.user.id+1)):
            RecordService.create_campus_records_from_excel(excel, context)

    def test_create_campus_records_with_bad_role(self):
        '''Should raise Error if get bad role.'''
        tup = tempfile.mkstemp()
        work_book = xlwt.Workbook()
        sheet = work_book.add_sheet(u'sheet1', cell_overwrite_ok=True)
        sheet.write(0, 1, self.campus_event.id)
        sheet.write(3, 2, self.user.id)
        sheet.write(3, 5, '6')
        user = mommy.make(User)
        context = {
            'user': user,
        }
        assign_perm('training_event.change_campusevent',
                    user, self.campus_event)
        mommy.make(EventCoefficient,
                   campus_event=self.campus_event,
                   role=EventCoefficient.ROLE_PARTICIPATOR)
        mommy.make(EventCoefficient,
                   campus_event=self.campus_event,
                   role=EventCoefficient.ROLE_EXPERT)
        work_book.save(tup[1])
        with open(tup[0], 'rb') as work_book:
            excel = work_book.read()

        with self.assertRaisesMessage(
                BadRequest,
                '第4行，不存在的参与形式'):
            RecordService.create_campus_records_from_excel(excel, context)

    def test_create_campus_records(self):
        '''Should return the number of created records.'''
        tup = tempfile.mkstemp()
        work_book = xlwt.Workbook()
        sheet = work_book.add_sheet(u'sheet1', cell_overwrite_ok=True)
        sheet.write(0, 1, self.campus_event.id)
        sheet.write(3, 2, self.user.id)
        sheet.write(3, 4, '参与')
        sheet.write(3, 5, '6')
        user = mommy.make(User)
        context = {
            'user': user,
        }
        assign_perm('training_event.change_campusevent',
                    user, self.campus_event)
        mommy.make(EventCoefficient,
                   campus_event=self.campus_event,
                   role=EventCoefficient.ROLE_PARTICIPATOR)
        mommy.make(EventCoefficient,
                   campus_event=self.campus_event,
                   role=EventCoefficient.ROLE_EXPERT)
        work_book.save(tup[1])
        with open(tup[0], 'rb') as work_book:
            excel = work_book.read()

        count = RecordService.create_campus_records_from_excel(excel, context)
        self.assertEqual(count, 1)

    def test_department_admin_review_no_record(self):
        '''Should raise BadRequest if no such record.'''
        campus_event = mommy.make(CampusEvent)
        record = mommy.make(Record,
                            campus_event=campus_event,
                            status=Record.STATUS_DEPARTMENT_ADMIN_APPROVED)
        user = mommy.make(get_user_model())
        with self.assertRaisesMessage(
                BadRequest, '无此培训记录！'):
            RecordService.department_admin_review(record.id, True, user)

    def test_department_admin_review_no_permission(self):
        '''Should raise BadRequest if no enough permission.'''
        off_campus_event = mommy.make(OffCampusEvent)
        record = mommy.make(Record,
                            off_campus_event=off_campus_event,
                            status=Record.STATUS_DEPARTMENT_ADMIN_APPROVED)
        user = mommy.make(get_user_model())
        with self.assertRaisesMessage(
                BadRequest, '无权更改！'):
            RecordService.department_admin_review(record.id, True, user)

    def test_department_admin_review_no_request_data(self):
        '''Should raise BadRequest if request data not has approve field.'''
        off_campus_event = mommy.make(OffCampusEvent)
        record = mommy.make(Record,
                            off_campus_event=off_campus_event,
                            status=Record.STATUS_SUBMITTED)
        user = mommy.make(get_user_model())
        with self.assertRaisesMessage(
                BadRequest, '请求无效！'):
            RecordService.department_admin_review(record.id, None, user)

    def test_department_admin_review_approve(self):
        '''Should change the status of off-campus training record.'''
        off_campus_event = mommy.make(OffCampusEvent)
        record = mommy.make(Record,
                            off_campus_event=off_campus_event,
                            status=Record.STATUS_SUBMITTED)
        user = mommy.make(get_user_model())
        result = RecordService.department_admin_review(record.id, True, user)

        self.assertEqual(result.status,
                         Record.STATUS_DEPARTMENT_ADMIN_APPROVED)

    def test_department_admin_review_reject(self):
        '''Should change the status of off-campus training record.'''
        off_campus_event = mommy.make(OffCampusEvent)
        record = mommy.make(Record,
                            off_campus_event=off_campus_event,
                            status=Record.STATUS_SUBMITTED)
        user = mommy.make(get_user_model())
        result = RecordService.department_admin_review(record.id, False, user)

        self.assertEqual(result.status,
                         Record.STATUS_DEPARTMENT_ADMIN_REJECTED)

    def test_school_admin_review_no_record(self):
        '''Should raise BadRequest if no such record.'''
        campus_event = mommy.make(CampusEvent)
        record = mommy.make(Record,
                            campus_event=campus_event,
                            status=Record.STATUS_SCHOOL_ADMIN_APPROVED)
        user = mommy.make(get_user_model())
        with self.assertRaisesMessage(
                BadRequest, '无此培训记录！'):
            RecordService.school_admin_review(record.id, True, user)

    def test_school_admin_review_no_permission(self):
        '''Should raise BadRequest if no enough permission.'''
        off_campus_event = mommy.make(OffCampusEvent)
        record = mommy.make(Record,
                            off_campus_event=off_campus_event,
                            status=Record.STATUS_SCHOOL_ADMIN_APPROVED)
        user = mommy.make(get_user_model())
        with self.assertRaisesMessage(
                BadRequest, '无权更改！'):
            RecordService.school_admin_review(record.id, True, user)

    def test_school_admin_review_no_request_data(self):
        '''Should raise BadRequest if request data not has approve field.'''
        off_campus_event = mommy.make(OffCampusEvent)
        record = mommy.make(Record,
                            off_campus_event=off_campus_event,
                            status=Record.STATUS_DEPARTMENT_ADMIN_APPROVED)
        user = mommy.make(get_user_model())
        with self.assertRaisesMessage(
                BadRequest, '请求无效！'):
            RecordService.school_admin_review(record.id, None, user)

    def test_school_admin_review_approve(self):
        '''Should change the status of off-campus training record.'''
        off_campus_event = mommy.make(OffCampusEvent)
        record = mommy.make(Record,
                            off_campus_event=off_campus_event,
                            status=Record.STATUS_DEPARTMENT_ADMIN_APPROVED)
        user = mommy.make(get_user_model())
        result = RecordService.school_admin_review(record.id, True, user)

        self.assertEqual(result.status, Record.STATUS_SCHOOL_ADMIN_APPROVED)

    def test_school_admin_review_reject(self):
        '''Should change the status of off-campus training record.'''
        off_campus_event = mommy.make(OffCampusEvent)
        record = mommy.make(Record,
                            off_campus_event=off_campus_event,
                            status=Record.STATUS_DEPARTMENT_ADMIN_APPROVED)
        user = mommy.make(get_user_model())
        result = RecordService.school_admin_review(record.id, False, user)

        self.assertEqual(result.status, Record.STATUS_SCHOOL_ADMIN_REJECTED)

    def test_close_record_no_record(self):
        '''Should raise BadRequest if no such record.'''
        campus_event = mommy.make(CampusEvent)
        record = mommy.make(Record,
                            campus_event=campus_event,
                            status=Record.STATUS_DEPARTMENT_ADMIN_APPROVED)
        user = mommy.make(get_user_model())
        with self.assertRaisesMessage(
                BadRequest, '无此培训记录！'):
            RecordService.close_record(record.id, user)

    def test_close_record_no_permission(self):
        '''Should raise BadRequest if no enough permission.'''
        off_campus_event = mommy.make(OffCampusEvent)
        record = mommy.make(Record,
                            off_campus_event=off_campus_event,
                            status=Record.STATUS_SCHOOL_ADMIN_APPROVED)
        user = mommy.make(get_user_model())
        with self.assertRaisesMessage(
                BadRequest, '无权更改！'):
            RecordService.close_record(record.id, user)

    def test_close_record_succeed(self):
        '''Should close the off-campus training record.'''
        off_campus_event = mommy.make(OffCampusEvent)
        record = mommy.make(Record,
                            off_campus_event=off_campus_event,
                            status=Record.STATUS_DEPARTMENT_ADMIN_APPROVED)
        user = mommy.make(get_user_model())
        result = RecordService.close_record(record.id, user)

        self.assertEqual(result.status, Record.STATUS_CLOSED)

    # pylint: disable=unused-variable
    def test_get_number_of_records_without_feedback(self):
        '''Should return the count of records which requiring feedback'''
        user = mommy.make(get_user_model())
        off_campus_event0 = mommy.make(OffCampusEvent)
        off_campus_event1 = mommy.make(OffCampusEvent)
        campus_event = mommy.make(CampusEvent)
        record0 = mommy.make(Record, user=user,
                             off_campus_event=off_campus_event0)
        record1 = mommy.make(Record, user=user,  # noqa
                             off_campus_event=off_campus_event1)
        record2 = mommy.make(Record, user=user,  # noqa
                             campus_event=campus_event,)
        CampusEventFeedbackService.create_feedback(record0, '123')

        result = RecordService.get_number_of_records_without_feedback(user)

        self.assertEqual(result, 1)


class TestCampusEventFeedbackService(TestCase):
    '''Test services provided by CampusEventFeedbackService.'''
    def test_create_feedback(self):
        '''Should create feedback and update the status.'''
        campus_event = mommy.make(CampusEvent)
        record = mommy.make(Record, campus_event=campus_event)
        CampusEventFeedbackService.create_feedback(record, '123')
        record = Record.objects.get(pk=record.id)

        self.assertEqual(CampusEventFeedback.objects.all().count(), 1)
        self.assertEqual(record.status, Record.STATUS_FEEDBACK_SUBMITTED)
