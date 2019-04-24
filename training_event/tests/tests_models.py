'''Unit tests for training_event models.'''
import math
from unittest.mock import patch

from django.test import TestCase
from django.utils.text import format_lazy as _f

from training_record.models import Record
from training_event.models import (
    CampusEvent, OffCampusEvent, Enrollment, EventCoefficient)


# pylint: disable=no-self-use
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


class TestEventCoefficient(TestCase):
    '''Unit tests for model EventCoefficient.'''
    def test_calculate_off_campus_event_workload(self):
        '''Should return 0 correctly.'''
        event_coefficient = EventCoefficient()
        record = Record()
        self.assertEqual(
            event_coefficient.calculate_off_campus_event_workload(record), 0)

    def test_calculate_campus_event_workload(self):
        '''Should return workload correctly.'''
        num_hours = 10.5
        campus_event = CampusEvent(num_hours=num_hours)

        def test_generate(campus_event, hours_option, workload_option, result):
            '''Should generate testcase correctly.'''
            event_coefficient = EventCoefficient(
                role=EventCoefficient.ROLE_PARTICIPATOR, coefficient=1,
                hours_option=hours_option, workload_option=workload_option,
                campus_event=campus_event)
            record = Record(campus_event=campus_event)
            self.assertAlmostEqual(
                event_coefficient.calculate_campus_event_workload(record),
                result)

        test_generate(campus_event, EventCoefficient.ROUND_METHOD_NONE,
                      EventCoefficient.ROUND_METHOD_NONE, num_hours)
        test_generate(campus_event, EventCoefficient.ROUND_METHOD_NONE,
                      EventCoefficient.ROUND_METHOD_CEIL, math.ceil(num_hours))
        test_generate(
            campus_event, EventCoefficient.ROUND_METHOD_NONE,
            EventCoefficient.ROUND_METHOD_FLOOR, math.floor(num_hours))
        test_generate(
            campus_event, EventCoefficient.ROUND_METHOD_NONE,
            EventCoefficient.ROUND_METHOD_DEFAULT, round(num_hours))

        test_generate(campus_event, EventCoefficient.ROUND_METHOD_CEIL,
                      EventCoefficient.ROUND_METHOD_NONE, math.ceil(num_hours))
        test_generate(
            campus_event, EventCoefficient.ROUND_METHOD_FLOOR,
            EventCoefficient.ROUND_METHOD_NONE, math.floor(num_hours))
        test_generate(
            campus_event, EventCoefficient.ROUND_METHOD_DEFAULT,
            EventCoefficient.ROUND_METHOD_NONE, round(num_hours))

    @patch(
        'training_event.models.EventCoefficient'
        '.calculate_campus_event_workload')
    def test_calculate_event_workload_campus_event(self, mocked):
        '''Should call calculate_campus_event_workload correctly.'''
        event_coefficient = EventCoefficient()
        campus_event = CampusEvent()
        record = Record(campus_event=campus_event)
        event_coefficient.calculate_event_workload(record)
        mocked.assert_called_with(record)

    @patch('training_event.models.EventCoefficient'
           '.calculate_off_campus_event_workload')
    def test_calculate_event_workload_off_campus_event(self, mocked):
        '''Should call calculate_event_workload correctly.'''
        event_coefficient = EventCoefficient()
        record = Record()
        event_coefficient.calculate_off_campus_event_workload(record)
        mocked.assert_called_with(record)
