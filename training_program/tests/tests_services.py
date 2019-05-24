'''Unit tests for training_program services.'''
from rest_framework.test import APITestCase
from django.http import HttpRequest
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from model_mommy import mommy

from training_program.models import Program
from training_program.services import ProgramService
from auth.models import Department
from auth.utils import assign_perm

User = get_user_model()


class TestProgramService(APITestCase):
    '''Test services provided by ProgramService.'''
    def setUp(self):
        self.user = mommy.make(User)
        self.group = mommy.make(Group, name="创新创业学院-管理员")
        self.depart = mommy.make(Department, name="创新创业学院")
        self.user.groups.add(self.group)
        self.data = {'name': '1', 'category': '2', 'department': self.depart}
        self.data1 = {'name': '2', 'category': '2', 'department': self.depart}
        self.request = HttpRequest()
        self.request.user = self.user
        self.context = {'request': self.request, 'data': ''}
        mommy.make(Group, name="个人权限")
        assign_perm('training_program.add_program', self.group)
        assign_perm('training_program.view_program', self.group)

    def test_create_program_admin(self):
        '''Should create training_program.'''
        ProgramService.create_program(self.data, self.context)

        count = Program.objects.all().count()
        self.assertEqual(count, 1)

    def test_update_program_admin(self):
        '''Should update training_program.'''
        program = ProgramService.create_program(self.data, self.context)
        program1 = ProgramService.update_program(program,
                                                 self.data1, self.context)

        self.assertEqual(program1.name, '2')

    def test_group_program(self):
        '''Should get group programs by department'''
        user = mommy.make(User)
        group = mommy.make(Group, name='大连理工大学-管理员')
        user.groups.add(group)
        department = mommy.make(Department, id=1, name='大连理工大学')
        program = mommy.make(Program, department=department)
        group_programs = ProgramService.get_grouped_programs_by_department(
            user)
        self.assertEqual(len(group_programs), 1)
        self.assertEqual(group_programs[0]['programs'][0]['id'], program.id)
        user = mommy.make(User)
        group_programs = ProgramService.get_grouped_programs_by_department(
            user)
        self.assertEqual(len(group_programs), 0)
