'''Unit tests for training_event services.'''
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.utils.timezone import now
from django.test import TestCase
from django.http import HttpRequest
from model_mommy import mommy
from infra.exceptions import BadRequest
from training_event.models import CampusEvent, Enrollment, EventCoefficient
from training_event.services import EnrollmentService, CampusEventService
from training_program.models import Program
from auth.models import Department
from auth.utils import assign_perm

User = get_user_model()


class TestCampusEventService(TestCase):
    '''Test services provided by CampusEventService.'''
    def setUp(self):
        self.user = mommy.make(User)
        self.group = mommy.make(Group, name="创新创业学院-管理员")
        self.depart = mommy.make(Department, name="创新创业学院")
        self.user.groups.add(self.group)
        program = mommy.make(Program)
        self.data = {
            "name": "1",
            "time": "2018-05-07T11:11:00+08:00",
            "location": "1",
            "num_hours": 1.0,
            "num_participants": 1,
            "deadline": "2019-05-09T01:11:00+08:00",
            "description": "1",
            "program": program,
        }
        self.coefficients = [
            {
                'id': 1,
                'role': 0,
                'hours_option': 1,
                'workload_option': 3,
                'coefficient': 1,
            },
            {
                'id': 2,
                'role': 1,
                'hours_option': 1,
                'workload_option': 3,
                'coefficient': 1,
            }
        ]
        self.request = HttpRequest()
        self.request.user = self.user
        self.context = {'request': self.request, 'data': ''}
        mommy.make(Group, name="个人权限")
        assign_perm('training_program.add_program', self.group)
        assign_perm('training_program.view_program', self.group)

    def test_review_campus_event(self):
        '''Should mark reviewed as True.'''
        event = mommy.make(CampusEvent)
        CampusEventService.review_campus_event(event, self.user)

        event = CampusEvent.objects.get(id=event.id)
        self.assertTrue(event.reviewed)

    def test_create_campus_event_admin(self):
        '''Should create campus_event.'''
        CampusEventService.create_campus_event(self.data,
                                               self.coefficients,
                                               self.context)
        count_program = Program.objects.all().count()
        count_event_coefficient = EventCoefficient.objects.all().count()
        self.assertEqual(count_program, 1)
        self.assertEqual(count_event_coefficient, 2)

    def test_update_campus_event(self):
        '''Should update campus event and coefficient.'''
        event = CampusEventService.create_campus_event(self.data,
                                                       self.coefficients,
                                                       self.context)
        self.data['name'] = '2'
        self.coefficients[0]['coefficient'] = 123
        event1 = CampusEventService.update_campus_event(event,
                                                        self.data,
                                                        self.coefficients,
                                                        self.context)

        self.assertEqual(event1.name, '2')


class TestEnrollmentService(TestCase):
    '''Test services provided by EnrollmentService.'''
    def setUp(self):
        self.event = mommy.make(CampusEvent, num_participants=0)
        self.user = mommy.make(User)
        self.group = mommy.make(Group, name="个人权限")
        self.user.groups.add(self.group)
        self.data = {'campus_event': self.event, 'user': self.user}
        assign_perm('training_event.add_enrollment', self.group)
        assign_perm('training_event.delete_enrollment', self.group)

    def test_create_enrollment_event_expired(self):
        '''Should raise BadRequest if event expired.'''
        self.event.deadline = now().replace(year=2018)
        self.event.save()
        with self.assertRaisesMessage(
                BadRequest, '报名时间已过'):
            EnrollmentService.create_enrollment(self.data)

    def test_create_enrollment_no_more_head_counts(self):
        '''Should raise BadRequest if no more head counts for CampusEvent.'''
        self.event.deadline = now().replace(year=2028)
        self.event.save()
        with self.assertRaisesMessage(
                BadRequest, '报名人数已满'):
            EnrollmentService.create_enrollment(self.data)

    def test_create_enrollment_user_in_data(self):
        '''Should create enrollment.'''
        self.event.num_participants = 10
        self.event.deadline = now().replace(year=2028)
        self.event.save()
        EnrollmentService.create_enrollment(self.data)

        count = Enrollment.objects.filter(user=self.user).count()

        self.assertEqual(count, 1)

    def test_get_user_enrollment_status(self):
        '''Should get user enrollment status.'''
        events = [mommy.make(CampusEvent) for _ in range(10)]
        expected_result = {}
        for idx, event in enumerate(events):
            if idx >= 3:
                mommy.make(Enrollment, user=self.user, campus_event=event)
                expected_result[event.id] = True
            else:
                expected_result[event.id] = False
        results = EnrollmentService.get_user_enrollment_status(
            events, self.user.id)
        self.assertEqual(results, expected_result)

    def test_get_user_enrollment_id(self):
        '''Should get user enrollment id.'''
        events = [mommy.make(CampusEvent) for _ in range(10)]
        expected_result = {}
        for idx, event in enumerate(events):
            if idx >= 3:
                obj = mommy.make(Enrollment, user=self.user,
                                 campus_event=event)
                expected_result[event.id] = obj.id
            else:
                expected_result[event.id] = None

        results = EnrollmentService.get_user_enrollment_id(
            events, self.user.id)
        self.assertEqual(results, expected_result)

    def test_delete_enrollment(self):
        '''Should delete enrollment.'''
        self.event.num_participants = 10
        self.event.num_enrolled = 2
        self.event.save()
        enrollment = mommy.make(Enrollment,
                                user=self.user, campus_event=self.event)
        EnrollmentService.delete_enrollment(enrollment)
        self.assertEqual(Enrollment.objects.count(), 0)

    def test_get_enrollments(self):
        '''Should get matched enrollments'''
        event = mommy.make(CampusEvent, id=1, num_participants=10)
        department = mommy.make(
            Department, name='大连理工大学', id=1)
        user = mommy.make(User, department=department)
        mommy.make(Enrollment, user=user, campus_event=event)
        assign_perm('training_event.change_campusevent', user, event)
        count = EnrollmentService.get_enrollments(
            1, context={'user': user}).count()
        self.assertEqual(count, 1)
