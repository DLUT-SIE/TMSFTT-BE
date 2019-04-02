'''Unit tests for training_event services.'''
from django.contrib.auth import get_user_model
from django.test import TestCase
from model_mommy import mommy

from infra.exceptions import BadRequest
from training_event.models import CampusEvent, Enrollment
from training_event.services import EnrollmentService


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
