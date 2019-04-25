'''Unit tests for training_event serializers.'''
from unittest.mock import patch

from django.test import TestCase

from training_event.serializers import EnrollmentSerailizer


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
