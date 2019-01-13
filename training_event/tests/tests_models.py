'''Unit tests for training_event models.'''
from unittest.mock import patch

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
    @patch('training_event.models.Enrollment.campus_event')
    @patch('training_event.models.Enrollment.user')
    def test_str(self, mocked_user, mocked_campus_event):
        '''Should render string correctly.'''
        name = 'event'
        mocked_campus_event.__str__.return_value = name
        user = 'user'
        mocked_user.__str__.return_value = user
        expected_str = _f('{} 报名 {} 的记录', user, name)
        enrollment = Enrollment()

        self.assertEqual(str(enrollment), expected_str)
