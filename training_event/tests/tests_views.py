'''Unit tests for training_event views.'''
from unittest.mock import patch
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.utils.timezone import now
from model_mommy import mommy
from rest_framework import status
from rest_framework.test import APITestCase

import training_program.models
import training_event.models


User = get_user_model()


class TestCampusEventViewSet(APITestCase):
    '''Unit tests for CampusEvent view.'''
    @classmethod
    def setUpTestData(cls):
        cls.user = mommy.make(User)

    def setUp(self):
        self.client.force_authenticate(self.user)

    def test_create_campus_event(self):
        '''CampusEvent should be created by POST request.'''
        program = mommy.make(training_program.models.Program)
        url = reverse('campusevent-list')
        name = 'event'
        time = now()
        location = 'location'
        num_hours = 10
        num_participants = 100
        data = {
            'name': name,
            'time': time,
            'location': location,
            'num_hours': num_hours,
            'num_participants': num_participants,
            'program': program.pk,
            'deadline': time,
        }

        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(training_event.models.CampusEvent.objects.count(), 1)
        self.assertEqual(training_event.models.CampusEvent.objects.get().name,
                         name)

    def test_list_campus_event(self):
        '''CampusEvents list should be accessed by GET request.'''
        url = reverse('campusevent-list')

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_delete_campus_event(self):
        '''CampusEvent should be deleted by DELETE request.'''
        campus_event = mommy.make(training_event.models.CampusEvent)
        url = reverse('campusevent-detail', args=(campus_event.pk,))

        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(training_event.models.CampusEvent.objects.count(), 0)

    def test_get_campus_event(self):
        '''CampusEvent should be accessed by GET request.'''
        campus_event = mommy.make(training_event.models.CampusEvent)
        url = reverse('campusevent-detail', args=(campus_event.pk,))

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('id', response.data)
        self.assertEqual(response.data['id'], campus_event.id)

    def test_update_campus_event(self):
        '''CampusEvent should be updated by PATCH request.'''
        name0 = 'campus_event0'
        name1 = 'campus_event1'
        campus_event = mommy.make(training_event.models.CampusEvent,
                                  name=name0)
        url = reverse('campusevent-detail', args=(campus_event.pk,))
        data = {'name': name1}

        response = self.client.patch(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('name', response.data)
        self.assertEqual(response.data['name'], name1)


class TestOffCampusEventViewSet(APITestCase):
    '''Unit tests for OffCampusEvent view.'''
    @classmethod
    def setUpTestData(cls):
        cls.user = mommy.make(User)

    def setUp(self):
        self.client.force_authenticate(self.user)

    def test_create_off_campus_event(self):
        '''OffCampusEvent should be created by POST request.'''
        url = reverse('offcampusevent-list')
        name = 'event'
        time = now()
        location = 'location'
        num_hours = 10
        num_participants = 100
        data = {
            'name': name,
            'time': time,
            'location': location,
            'num_hours': num_hours,
            'num_participants': num_participants,
        }

        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(
            training_event.models.OffCampusEvent.objects.count(), 1)
        self.assertEqual(
            training_event.models.OffCampusEvent.objects.get().name, name)

    def test_list_off_campus_event(self):
        '''OffCampusEvents list should be accessed by GET request.'''
        url = reverse('offcampusevent-list')

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_delete_off_campus_event(self):
        '''OffCampusEvent should be deleted by DELETE request.'''
        off_campus_event = mommy.make(training_event.models.OffCampusEvent)
        url = reverse('offcampusevent-detail', args=(off_campus_event.pk,))

        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(
            training_event.models.OffCampusEvent.objects.count(), 0)

    def test_get_off_campus_event(self):
        '''OffCampusEvent should be accessed by GET request.'''
        off_campus_event = mommy.make(training_event.models.OffCampusEvent)
        url = reverse('offcampusevent-detail', args=(off_campus_event.pk,))

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('id', response.data)
        self.assertEqual(response.data['id'], off_campus_event.id)

    def test_update_off_campus_event(self):
        '''OffCampusEvent should be updated by PATCH request.'''
        name0 = 'off_campus_event0'
        name1 = 'off_campus_event1'
        off_campus_event = mommy.make(training_event.models.OffCampusEvent,
                                      name=name0)
        url = reverse('offcampusevent-detail', args=(off_campus_event.pk,))
        data = {'name': name1}

        response = self.client.patch(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('name', response.data)
        self.assertEqual(response.data['name'], name1)


class TestEnrollmentViewSet(APITestCase):
    '''Unit tests for Enrollment view.'''
    @classmethod
    def setUpTestData(cls):
        cls.user = mommy.make(User)

    def setUp(self):
        self.client.force_authenticate(self.user)

    def test_create_enrollment(self):
        '''Enrollment should be created by POST request.'''
        user = mommy.make(User)
        campus_event = mommy.make(training_event.models.CampusEvent)
        url = reverse('enrollment-list')
        data = {
            'campus_event': campus_event.pk,
            'user': user.pk,
        }

        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(
            training_event.models.Enrollment.objects.count(), 1)
        obj = training_event.models.Enrollment.objects.get()
        self.assertEqual(obj.campus_event.pk, campus_event.pk)
        self.assertEqual(obj.user.pk, user.pk)

    def test_list_enrollment(self):
        '''Enrollments list should be accessed by GET request.'''
        url = reverse('enrollment-list')

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    @patch('training_event.views.EnrollmentService')
    def test_delete_enrollment(self, mocked_service):
        '''Enrollment should be deleted by DELETE request.'''
        user = mommy.make(User)
        event = mommy.make(training_event.models.CampusEvent,
                           num_participants=0)
        event.num_participants = 10
        event.num_enrolled = 2
        event.save()
        enrollment = mommy.make(training_event.models.Enrollment,
                                user=user, campus_event=event)

        url = reverse('enrollment-detail', args=(enrollment.pk,))
        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        mocked_service.delete_enrollment.assert_called_with(enrollment)

    def test_get_enrollment(self):
        '''Enrollment should be accessed by GET request.'''
        enrollment = mommy.make(training_event.models.Enrollment)
        url = reverse('enrollment-detail', args=(enrollment.pk,))

        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('id', response.data)
        self.assertEqual(response.data['id'], enrollment.id)

    def test_update_enrollment(self):
        '''Enrollment should NOT be updated by PATCH request.'''
        enrollment = mommy.make(training_event.models.Enrollment)
        url = reverse('enrollment-detail', args=(enrollment.pk,))
        data = {}

        response = self.client.patch(url, data, format='json')

        self.assertEqual(response.status_code,
                         status.HTTP_405_METHOD_NOT_ALLOWED)


class TestWorkloadFileView(APITestCase):
    '''Unit tests for WorkloadFileView.'''

    @classmethod
    def setUpTestData(cls):
        cls.user = mommy.make(User)

    def test_post(self):
        '''should return 201 when successed'''
        url = reverse('download-workload')
        self.client.force_authenticate(user=self.user)  # pylint: disable=E1101
        data = {}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    @patch('training_event.views.EnrollmentService')
    def test_get_enrollment_status(self, mocked_service):
        '''Should get enrollemnts status according to request.'''
        user = mommy.make(get_user_model())
        url = reverse('enrollments-actions-get-enrollment-status')
        mocked_service.get_user_enrollment_status.return_value = [
            {
                "id": 1,
                "enrolled": False
            },
            {
                "id": 2,
                "enrolled": False
            },
            {
                "id": 3,
                "enrolled": True
            },
            {
                "id": 4,
                "enrolled": True
            },
        ]
        self.client.force_authenticate(user)
        event_list = [1, 2, 3, 4, 5]
        response = self.client.get(url, {'event': event_list})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
