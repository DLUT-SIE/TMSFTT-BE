'''Unit tests for training_event serializers.'''
from django.test import TestCase

import training_event.serializers as serializers
import training_event.models as models


class TestCampusEventSerializer(TestCase):
    '''Unit tests for serializer of CampusEvent.'''
    def test_fields_equal(self):
        '''Serializer should return fields of CampusEvent correctly.'''
        campus_event = models.CampusEvent()
        expected_keys = {
            'id', 'create_time', 'update_time', 'name', 'time',
            'location', 'num_hours', 'num_participants',
            'program', 'num_enrolled', 'description',
        }

        keys = set(serializers.CampusEventSerializer(
            campus_event).data.keys())
        self.assertEqual(keys, expected_keys)


class TestOffCampusEventSerializer(TestCase):
    '''Unit tests for serializer of OffCampusEvent.'''
    def test_fields_equal(self):
        '''Serializer should return fields of OffCampusEvent correctly.'''
        off_campus_event = models.OffCampusEvent()
        expected_keys = {
            'id', 'create_time', 'update_time', 'name', 'time',
            'location', 'num_hours', 'num_participants',
        }

        keys = set(serializers.OffCampusEventSerializer(
            off_campus_event).data.keys())
        self.assertEqual(keys, expected_keys)


class TestEnrollmentSerializer(TestCase):
    '''Unit tests for serializer of Enrollment.'''
    def test_fields_equal(self):
        '''Serializer should return fields of Enrollment correctly.'''
        enrollment = models.Enrollment()
        expected_keys = {
            'id', 'create_time', 'campus_event', 'user',
            'enroll_method', 'is_participated',
        }

        keys = set(serializers.EnrollmentSerailizer(enrollment).data.keys())
        self.assertEqual(keys, expected_keys)
