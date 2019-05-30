'''Unit tests for attendance sheet service.'''
from rest_framework.test import APITestCase
from model_mommy import mommy
from training_event.models import (
    CampusEvent, Enrollment
)
from data_warehouse.services.attendance_sheet_service import (
    AttendanceSheetService)
from auth.models import User, Department


class TestAttendanceSheetService(APITestCase):
    '''Unit tests for attendance sheet service.'''
    def test_get_enrollment(self):
        '''Should get matched enrollment'''
        event = mommy.make(CampusEvent, id=1, num_participants=10)
        department = mommy.make(
            Department, name='大连理工大学', id=1)
        user = mommy.make(User, department=department)
        mommy.make(Enrollment, user=user, campus_event=event)
        count = AttendanceSheetService.get_enrollment(1).count()
        self.assertEqual(count, 1)
