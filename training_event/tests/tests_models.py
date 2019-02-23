'''Unit tests for training_event models.'''
from django.test import TestCase
from django.utils.text import format_lazy as _f

from training_event.models import (CampusEvent, OffCampusEvent, Enrollment)


class TestCampusEvent(TestCase):
    '''Unit tests for model CampusEvent.'''
    def test_str(self):
        '''Should render string correctly.'''
        name = 'name'
        campus_event = CampusEvent(name=name)

        self.assertEqual(str(campus_event), name)


class TestOffCampusEvent(TestCase):
    '''Unit tests for model OffCampusEvent.'''
    def test_str(self):
        '''Should render string correctly.'''
        name = 'name'
        off_campus_event = OffCampusEvent(name=name)

        self.assertEqual(str(off_campus_event), name)


class TestEnrollment(TestCase):
    '''Unit tests for model Enrollment.'''
    def test_str(self):
        '''Should render string correctly.'''
        campus_event_id = 123
        user_id = 456
        expected_str = _f('{} 报名 {} 的记录', user_id, campus_event_id)
        enrollment = Enrollment(
            campus_event_id=campus_event_id,
            user_id=user_id,
        )

        self.assertEqual(str(enrollment), expected_str)
