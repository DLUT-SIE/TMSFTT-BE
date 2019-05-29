'''Unit tests for attendance sheet service.'''
from rest_framework.test import APITestCase
from model_mommy import mommy
from training_event.models import (
    CampusEvent, Enrollment
)
from data_warehouse.services.attendance_sheet_service import (
    AttendanceSheetService)
from auth.models import User


class TestAttendanceSheetService(APITestCase):
    '''Unit tests for attendance sheet service.'''
    def setUp(self):
        self.event = mommy.make(CampusEvent, id=1, num_participants=10)
        self.user = mommy.make(User)

    def test_get_event(self):
        '''Should return matched event.'''
        data = AttendanceSheetService.get_event(1)
        self.assertEqual(data.id, 1)

    def test_get_user(self):
        '''Should return matched user.'''
        mommy.make(Enrollment, user=self.user, campus_event=self.event)
        count = AttendanceSheetService.get_user(1).count()
        self.assertEqual(count, 1)
