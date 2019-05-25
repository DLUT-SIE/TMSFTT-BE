'''Unit tests for training_event views.'''
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.urls import reverse
from django.utils.timezone import now
from model_mommy import mommy
from rest_framework import status
from rest_framework.test import APITestCase

import training_program.models
import training_event.models
import auth.models
from auth.utils import assign_perm
from auth.services import PermissionService

User = get_user_model()


class TestCampusEventViewSet(APITestCase):
    '''Unit tests for CampusEvent view.'''
    @classmethod
    def setUpTestData(cls):
        cls.depart = mommy.make(auth.models.Department, name="创新创业学院")
        cls.user = mommy.make(User, department=cls.depart)
        cls.group = mommy.make(Group, name="创新创业学院-管理员")
        cls.user.groups.add(cls.group)
        mommy.make(Group, name="个人权限")
        assign_perm('training_event.add_campusevent', cls.group)
        assign_perm('training_event.view_campusevent', cls.group)
        assign_perm('training_event.review_campusevent', cls.group)
        assign_perm('training_event.change_campusevent', cls.group)
        assign_perm('training_event.delete_campusevent', cls.group)

    def setUp(self):
        self.client.force_authenticate(self.user)

    def test_review_event(self):
        '''Should mark event as reviewed.'''
        event = mommy.make(training_event.models.CampusEvent)
        assign_perm('training_event.view_campusevent', self.group, event)
        assign_perm('training_event.review_campusevent', self.group, event)

        url = reverse('campusevent-review-event', args=(event.id,))

        response = self.client.post(url, {}, format='json')

        event = training_event.models.CampusEvent.objects.get(id=event.id)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(event.reviewed)

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
            'coefficients': [
                {
                    'role': 0,
                    'hours_option': 1,
                    'workload_option': 3,
                    'coefficient': 1,
                },
                {
                    'role': 1,
                    'hours_option': 1,
                    'workload_option': 3,
                    'coefficient': 1,
                }
            ]
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
        PermissionService.assign_object_permissions(self.user, campus_event)
        url = reverse('campusevent-detail', args=(campus_event.pk,))

        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(training_event.models.CampusEvent.objects.count(), 0)

    def test_get_campus_event(self):
        '''CampusEvent should be accessed by GET request.'''
        campus_event = mommy.make(training_event.models.CampusEvent)
        PermissionService.assign_object_permissions(self.user, campus_event)
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
        PermissionService.assign_object_permissions(self.user, campus_event)
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
        cls.group = mommy.make(Group, name="个人权限")
        cls.user.groups.add(cls.group)
        assign_perm('training_event.add_enrollment', cls.group)
        assign_perm('training_event.delete_enrollment', cls.group)

    def setUp(self):
        self.client.force_authenticate(self.user)

    def test_create_enrollment(self):
        '''Enrollment should be created by POST request.'''
        campus_event = mommy.make(training_event.models.CampusEvent)
        url = reverse('enrollment-list')
        data = {
            'campus_event': campus_event.pk,
        }

        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(
            training_event.models.Enrollment.objects.count(), 1)
        obj = training_event.models.Enrollment.objects.get()
        self.assertEqual(obj.campus_event.pk, campus_event.pk)

    def test_list_enrollment(self):
        '''Enrollments list should be accessed by GET request.'''
        url = reverse('enrollment-list')

        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_enrollment(self):
        '''Enrollment should be deleted by DELETE request.'''
        user = mommy.make(User)
        event = mommy.make(training_event.models.CampusEvent,
                           num_participants=0)
        event.num_participants = 10
        event.num_enrolled = 2
        event.save()
        enrollment = mommy.make(training_event.models.Enrollment,
                                user=user, campus_event=event)
        PermissionService.assign_object_permissions(self.user, enrollment)
        url = reverse('enrollment-detail', args=(enrollment.pk,))
        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_get_enrollment(self):
        '''Enrollment should be accessed by GET request.'''
        enrollment = mommy.make(training_event.models.Enrollment)
        url = reverse('enrollment-detail', args=(enrollment.pk,))
        PermissionService.assign_object_permissions(self.user, enrollment)

        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_update_enrollment(self):
        '''Enrollment should NOT be updated by PATCH request.'''
        enrollment = mommy.make(training_event.models.Enrollment)
        url = reverse('enrollment-detail', args=(enrollment.pk,))
        data = {}

        response = self.client.patch(url, data, format='json')

        self.assertEqual(response.status_code,
                         status.HTTP_404_NOT_FOUND)


class TestEventCoefficientRoundChoicesViewSet(APITestCase):
    '''Unit tests for EventCoefficientRoundChoicesViewSet'''

    def test_event_coefficient_round_choice(self):
        '''Should get event coefficient round choice according to request.'''
        user = mommy.make(get_user_model())
        url = reverse('round-choices')
        self.client.force_authenticate(user)
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_role_choices(self):
        '''Should return the whole role choices'''
        user = mommy.make(User)
        group = mommy.make(Group, name="创新创业学院-管理员")
        user.groups.add(group)
        url = reverse('role-choices')

        self.client.force_authenticate(user)
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
