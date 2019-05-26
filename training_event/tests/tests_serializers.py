'''Unit tests for training_event serializers.'''
from unittest.mock import patch, Mock

from django.test import TestCase
from django.utils.timezone import now
from rest_framework import serializers

from model_mommy import mommy

from training_event.serializers import (
    EnrollmentSerailizer,
    CampusEventSerializer,
    ReadOnlyCampusEventSerializer)
from training_event.models import CampusEvent


class TestCampusEventSerializer(TestCase):
    '''Unit tests for serializer of CampusEvent.'''

    def test_creating_event_get_enrollment_status(self):
        '''should get enrollments status when serializer events.'''
        event = mommy.make(CampusEvent)
        events = [event, event]
        serializer = ReadOnlyCampusEventSerializer(events, many=True)
        serializer.context['request'] = Mock()
        serializer.context['request'].user = 23
        data = serializer.data
        self.assertIn('expired', data[0])

    def test_expired_cause_by_no_more_head_counts(self):
        '''Should be expired if no more head counts for enrolling.'''
        event = mommy.make(CampusEvent, num_enrolled=10, num_participants=10)
        request = Mock()
        request.user = 23
        context = {
            'request': request
        }
        data = ReadOnlyCampusEventSerializer(event, context=context).data

        self.assertTrue(data['expired'], data)

    def test_expired_cause_by_deadline(self):
        '''Should be expired if passed deadline.'''
        event = mommy.make(CampusEvent, deadline=now().replace(year=2018))
        request = Mock()
        request.user = 23
        context = {
            'request': request
        }
        data = ReadOnlyCampusEventSerializer(event, context=context).data

        self.assertTrue(data['expired'], data)

    def test_validate_coefficients_update_reviewed(self):
        '''
        Should raise ValidationError if non-school-admin user tries to
        update reviewed coefficients.
        '''
        event = mommy.make(CampusEvent, reviewed=True)
        request = Mock()
        user = Mock()
        user.is_school_admin = False
        request.user = user
        context = {
            'request': request
        }
        serializer = CampusEventSerializer(event, context=context)
        with self.assertRaises(serializers.ValidationError):
            serializer.validate_coefficients({})

    def test_validate_coefficients_update(self):
        '''Should skip tests if event is not reviewed.'''
        event = mommy.make(CampusEvent, reviewed=False)
        request = Mock()
        user = Mock()
        user.is_school_admin = False
        request.user = user
        context = {
            'request': request
        }
        serializer = CampusEventSerializer(event, context=context)
        data = serializer.validate_coefficients({})

        self.assertIsInstance(data, dict)

    def test_get_enrollment_id(self):
        '''should get enrollments id when serialier events.'''
        event = mommy.make(CampusEvent)
        events = [event, event]
        serializer = ReadOnlyCampusEventSerializer(events, many=True)
        serializer.context['request'] = Mock()
        serializer.context['request'].user = 23
        data = serializer.data
        self.assertIn('enrollment_id', data[0])

    @patch('training_event.serializers.CampusEventService')
    def test_update(self, mocked_service):
        '''should update event and coefficient.'''
        serializer = CampusEventSerializer()
        data = {
            'coefficients': [
                {
                    'role': 0,
                },
                {
                    'role': 1,
                }
            ]
        }
        serializer.update(1, data)
        mocked_service.update_campus_event.assert_called()


class TestEnrollmentSerializer(TestCase):
    '''Unit tests for serializer of Enrollment.'''
    @patch('training_event.serializers.EnrollmentService')
    def test_should_invoke_service_when_creating_enrollment(
            self, mocked_service):
        '''Should invoke EnrollmentService to create instance.'''
        serializer = EnrollmentSerailizer()
        data = {'user': 123}
        serializer.create(data)
        mocked_service.create_enrollment.assert_called_with(data)
