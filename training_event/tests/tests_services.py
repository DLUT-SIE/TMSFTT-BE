'''Unit tests for training_event services.'''
import xlrd

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.utils.timezone import now
from model_mommy import mommy

from infra.exceptions import BadRequest
from training_event.models import (
    CampusEvent, Enrollment, EventCoefficient, OffCampusEvent)
from training_event.services import (
    EnrollmentService, CoefficientCalculationService)
from training_record.models import Record
from auth.models import Department


User = get_user_model()


class TestEnrollmentService(TestCase):
    '''Test services provided by EnrollmentService.'''
    def setUp(self):
        self.event = mommy.make(CampusEvent, num_participants=0)
        self.user = mommy.make(User)
        self.data = {'campus_event': self.event, 'user': self.user}

    def test_create_enrollment_no_more_head_counts(self):
        '''Should raise BadRequest if no more head counts for CampusEvent.'''
        with self.assertRaisesMessage(
                BadRequest, '报名人数已满'):
            EnrollmentService.create_enrollment(self.data)

    def test_create_enrollment(self):
        '''Should create enrollment.'''
        self.event.num_participants = 10
        self.event.save()

        EnrollmentService.create_enrollment(self.data)

        count = Enrollment.objects.filter(user=self.user).count()

        self.assertEqual(count, 1)


class TestCoefficientCalculationService(TestCase):
    '''Test services provided by EnrollmentService.'''
    NUM_HOURS = 10
    RECORDS_NUMS = 10

    @classmethod
    def setUpTestData(cls):

        cls.off_campus_event = mommy.make(OffCampusEvent, time=now())
        cls.campus_event = mommy.make(CampusEvent, num_hours=cls.NUM_HOURS,
                                      time=now())
        cls.department = mommy.make(Department)
        cls.user = mommy.make(User, department=cls.department)
        cls.event_coefficient = mommy.make(
            EventCoefficient, campus_event=cls.campus_event, coefficient=1,
            hours_option=EventCoefficient.ROUND_METHOD_CEIL,
            workload_option=EventCoefficient.ROUND_METHOD_CEIL,)

        cls.campus_records = [mommy.make(
            Record, event_coefficient=cls.event_coefficient, user=cls.user,
            campus_event=cls.campus_event) for _ in range(cls.RECORDS_NUMS)]

        cls.off_campus_record = mommy.make(
            Record, event_coefficient=cls.event_coefficient,
            off_campus_event=cls.off_campus_event, user=cls.user)
        cls.workload = 100
        cls.workload_dict = {cls.user: cls.workload}
        cls.filename = 'testfile'

    def test_calculate_workload_by_query(self):
        '''Should return workload by query'''
        self.assertEqual(
            CoefficientCalculationService.calculate_workload_by_query(
                department=self.department)[self.user],
            self.NUM_HOURS * self.RECORDS_NUMS)

    def test_generate_workload_excel_from_data(self):
        '''Should generate excel correctly'''
        path = (CoefficientCalculationService
                .generate_workload_excel_from_data(
                    self.workload_dict, self.filename)
                )
        workbook = xlrd.open_workbook(path)
        sheet = workbook.sheet_by_name(
            CoefficientCalculationService.WORKLOAD_SHEET_NAME)
        row = 0
        for col, title in enumerate(
                CoefficientCalculationService.WORKLOAD_SHEET_TITLE):
            self.assertEqual(title, sheet.cell_value(row, col))
        row += 1
        self.assertEqual(sheet.cell_value(row, 0), row)
        self.assertEqual(sheet.cell_value(row, 1), self.user.department.name)
        self.assertEqual(sheet.cell_value(row, 2), self.user.first_name)
        self.assertEqual(sheet.cell_value(row, 3), self.workload)
