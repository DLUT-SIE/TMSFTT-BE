'''Unit tests for training_event serializers.'''
from unittest.mock import patch, Mock

from django.test import TestCase
from django.utils.timezone import now

from model_mommy import mommy

from training_event.serializers import (
    EnrollmentSerailizer, CampusEventSerializer)
from training_event.models import CampusEvent


class TestCampusEventSerializer(TestCase):
    '''Unit tests for serializer of CampusEvent.'''

    def test_creating_event_get_enrollment_status(self):
        '''should get enrollments status when serializer events.'''
        event = mommy.make(CampusEvent)
        events = [event, event]
        serializer = CampusEventSerializer(events, many=True)
        serializer.context['request'] = Mock()
        serializer.context['request'].user = 23
        data = serializer.data
        self.assertIn('expired', data[0])

    def test_expired_cause_by_no_more_head_counts(self):
        '''Should be expired if no more head counts for enrolling.'''
        event = mommy.make(CampusEvent, num_enrolled=10, num_participants=10)
        data = CampusEventSerializer(event).data

        self.assertTrue(data['expired'], data)

    def test_expired_cause_by_deadline(self):
        '''Should be expired if passed deadline.'''
        event = mommy.make(CampusEvent, deadline=now().replace(year=2018))
        data = CampusEventSerializer(event).data

        self.assertTrue(data['expired'], data)

    def test_get_enrollment_id(self):
        '''should get enrollments id when serialier events.'''
        event = mommy.make(CampusEvent)
        events = [event, event]
        serializer = CampusEventSerializer(events, many=True)
        serializer.context['request'] = Mock()
        serializer.context['request'].user = 23
        data = serializer.data
        self.assertIn('enrollment_id', data[0])


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
