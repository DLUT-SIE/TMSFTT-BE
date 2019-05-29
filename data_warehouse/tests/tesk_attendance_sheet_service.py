'''Unit tests for attendance sheet service.'''
from rest_framework.test import APITestCase
from training_event.models import (
    CampusEvent, Enrollment
)
from data_warehouse.services.training_record_service import (
    AttendanceSheetService)
from model_mommy import mommy
from auth.models import User

class TestAttendanceSheetService(APITestCase):
    '''Unit tests for attendance sheet service.'''
    def setUp(slef):
        self.event = mommy.make(CampusEvent, id=1 ,num_participants=10)
        self.user = mommy.make(User)
        self.data = {'campus_event': self.event, 'user': self.user}
    def test_get_event(self):
        '''Should return matched event.'''
        count = CampusEvent.objects.filter(id=1).count()
        self.assertEqual(count, 1)
    def test_get_user(self):
        '''Should return matched user.'''
        mommy.make(Enrollment, user=self.user, campus_event=event)
        count = Enrollment.objects.filter(user=self.user).count()
        self.assertEqual(count, 1)


