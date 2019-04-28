'''Unit tests for training_record services.'''
import io
import tempfile
import xlwt

from django.test import TestCase
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import InMemoryUploadedFile
from model_mommy import mommy

from infra.exceptions import BadRequest
from training_record.models import (
    RecordContent, RecordAttachment, CampusEventFeedback, Record)
from training_record.services import RecordService, CampusEventFeedbackService
from training_event.models import CampusEvent, OffCampusEvent, EventCoefficient


User = get_user_model()


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
        cls.event_coefficient = mommy.make(EventCoefficient)

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
            off_campus_event=self.off_campus_event,
            user=user,
            contents=None,
            attachments=None,
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
            off_campus_event=self.off_campus_event,
            user=user,
            contents=self.contents,
            attachments=self.attachments,
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
            RecordService.create_campus_records_from_excel(tup[0])

    def test_create_campus_records_bad_event_id(self):
        '''Should raise Error if get invalid event id.'''
        tup = tempfile.mkstemp()
        work_book = xlwt.Workbook()
        sheet = work_book.add_sheet(u'sheet1', cell_overwrite_ok=True)
        sheet.write(0, 0, self.campus_event.id+1)
        work_book.save(tup[1])
        with open(tup[0], 'rb') as work_book:
            excel = work_book.read()
        with self.assertRaisesMessage(
                BadRequest, '编号为'+str(self.campus_event.id+1)+'的活动不存在'):
            RecordService.create_campus_records_from_excel(excel)

    def test_create_campus_records_bad_user_id(self):
        '''Should raise Error if get invalid user id.'''
        tup = tempfile.mkstemp()
        work_book = xlwt.Workbook()
        sheet = work_book.add_sheet(u'sheet1', cell_overwrite_ok=True)
        sheet.write(0, 0, self.campus_event.id)
        sheet.write(1, 0, self.user.id+1)
        work_book.save(tup[1])
        with open(tup[0], 'rb') as work_book:
            excel = work_book.read()
        with self.assertRaisesMessage(
                BadRequest, '编号为'+str(self.user.id+1)+'的用户不存在'):
            RecordService.create_campus_records_from_excel(excel)

    def test_create_campus_records_bad_event_coefficient_id(self):
        '''Should raise Error if get invalid event_coefficient id.'''
        tup = tempfile.mkstemp()
        work_book = xlwt.Workbook()
        sheet = work_book.add_sheet(u'sheet1', cell_overwrite_ok=True)
        sheet.write(0, 0, self.campus_event.id)
        sheet.write(1, 0, self.user.id)
        sheet.write(1, 1, self.event_coefficient.id + 1)
        work_book.save(tup[1])
        with open(tup[0], 'rb') as work_book:
            excel = work_book.read()
        with self.assertRaisesMessage(
                BadRequest,
                '编号为' + str(self.event_coefficient.id + 1) +
                '的活动系数不存在'):
            RecordService.create_campus_records_from_excel(excel)

    def test_create_campus_records(self):
        '''Should return the number of created records.'''
        tup = tempfile.mkstemp()
        work_book = xlwt.Workbook()
        sheet = work_book.add_sheet(u'sheet1', cell_overwrite_ok=True)
        sheet.write(0, 0, self.campus_event.id)
        sheet.write(1, 0, self.user.id)
        sheet.write(1, 1, self.event_coefficient.id)
        work_book.save(tup[1])
        with open(tup[0], 'rb') as work_book:
            excel = work_book.read()

        count = RecordService.create_campus_records_from_excel(excel)
        self.assertEqual(count, 1)

    def test_department_admin_review_no_record(self):
        '''Should raise BadRequest if no enough permission.'''
        campus_event = mommy.make(CampusEvent)
        record = mommy.make(Record,
                            campus_event=campus_event,
                            status=Record.STATUS_DEPARTMENT_ADMIN_APPROVED)
        with self.assertRaisesMessage(
                BadRequest, '无此培训记录！'):
            RecordService.department_admin_review(record.id, True)

    def test_department_admin_review_no_permission(self):
        '''Should raise BadRequest if no enough permission.'''
        off_campus_event = mommy.make(OffCampusEvent)
        record = mommy.make(Record,
                            off_campus_event=off_campus_event,
                            status=Record.STATUS_DEPARTMENT_ADMIN_APPROVED)
        with self.assertRaisesMessage(
                BadRequest, '无权更改！'):
            RecordService.department_admin_review(record.id, True)

    def test_department_admin_review_approve(self):
        '''Should change the status of off-campus training record.'''
        off_campus_event = mommy.make(OffCampusEvent)
        record = mommy.make(Record,
                            off_campus_event=off_campus_event,
                            status=Record.STATUS_SUBMITTED)
        result = RecordService.department_admin_review(record.id, True)

        self.assertEqual(result.status,
                         Record.STATUS_DEPARTMENT_ADMIN_APPROVED)

    def test_department_admin_review_reject(self):
        '''Should change the status of off-campus training record.'''
        off_campus_event = mommy.make(OffCampusEvent)
        record = mommy.make(Record,
                            off_campus_event=off_campus_event,
                            status=Record.STATUS_SUBMITTED)
        result = RecordService.department_admin_review(record.id, False)

        self.assertEqual(result.status,
                         Record.STATUS_DEPARTMENT_ADMIN_REJECTED)

    def test_school_admin_review_no_record(self):
        '''Should raise BadRequest if no enough permission.'''
        campus_event = mommy.make(CampusEvent)
        record = mommy.make(Record,
                            campus_event=campus_event,
                            status=Record.STATUS_SCHOOL_ADMIN_APPROVED)
        with self.assertRaisesMessage(
                BadRequest, '无此培训记录！'):
            RecordService.school_admin_review(record.id, True)

    def test_school_admin_review_no_permission(self):
        '''Should raise BadRequest if no enough permission.'''
        off_campus_event = mommy.make(OffCampusEvent)
        record = mommy.make(Record,
                            off_campus_event=off_campus_event,
                            status=Record.STATUS_SCHOOL_ADMIN_APPROVED)
        with self.assertRaisesMessage(
                BadRequest, '无权更改！'):
            RecordService.school_admin_review(record.id, True)

    def test_school_admin_review_approve(self):
        '''Should change the status of off-campus training record.'''
        off_campus_event = mommy.make(OffCampusEvent)
        record = mommy.make(Record,
                            off_campus_event=off_campus_event,
                            status=Record.STATUS_DEPARTMENT_ADMIN_APPROVED)
        result = RecordService.school_admin_review(record.id, True)

        self.assertEqual(result.status, Record.STATUS_SCHOOL_ADMIN_APPROVED)

    def test_school_admin_review_reject(self):
        '''Should change the status of off-campus training record.'''
        off_campus_event = mommy.make(OffCampusEvent)
        record = mommy.make(Record,
                            off_campus_event=off_campus_event,
                            status=Record.STATUS_DEPARTMENT_ADMIN_APPROVED)
        result = RecordService.school_admin_review(record.id, False)

        self.assertEqual(result.status, Record.STATUS_SUBMITTED)


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
