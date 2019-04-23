'''Unit tests for Celery tasks.'''
from unittest.mock import patch, Mock
from django.test import TestCase
from django.db import models
from model_mommy import mommy

from auth.models import (
    User, Department, DepartmentInformation, TeacherInformation)
from auth.tasks import (
    _update_from_department_information,
    _update_from_teacher_information,
    update_teachers_and_departments_information
)


# pylint: disable=no-self-use
class TestUpdateTeachersAndDepartmentsInformation(TestCase):
    '''Unit tests for syncing from provided data.'''

    @patch('auth.tasks.prod_logger')
    @patch('auth.tasks._update_from_department_information')
    @patch('auth.tasks._update_from_teacher_information')
    def test_call_update_functions(
            self, mocked_teacher_update_func, mocked_department_update_func,
            mocked_prod_logger):
        '''Should call update functions.'''
        dwid_to_department = Mock()
        mocked_department_update_func.return_value = dwid_to_department

        update_teachers_and_departments_information()

        mocked_department_update_func.assert_called()
        mocked_teacher_update_func.assert_called_with(dwid_to_department)
        mocked_prod_logger.exception.assert_not_called()

    @patch('auth.tasks.prod_logger')
    @patch('auth.tasks._update_from_department_information')
    @patch('auth.tasks._update_from_teacher_information')
    def test_logging_if_update_failed(
            self, _, mocked_department_update_func, mocked_prod_logger):
        '''Should call update functions.'''
        mocked_department_update_func.side_effect = Exception('Oops')

        update_teachers_and_departments_information()

        mocked_department_update_func.assert_called()
        mocked_prod_logger.exception.assert_called_with(
            '教师信息或部门信息更新失败')

    @patch('auth.models.DepartmentInformation.save',
           models.Model.save)
    def test_update_from_department_information(self):
        '''Should update department from department information.'''
        num_departments = 10
        infos = [mommy.make(DepartmentInformation,
                            dwid=f'{idx}',
                            dwmc=f'Department{idx}', _fill_optional=True)
                 for idx in range(num_departments)]

        dwid_to_department = _update_from_department_information()

        departments = Department.objects.all().order_by('raw_department_id')
        self.assertEqual(len(departments), num_departments)
        self.assertEqual(len(dwid_to_department), num_departments)

        for info, department in zip(infos, departments):
            self.assertEqual(info.dwmc, department.name)
            self.assertEqual(info.dwid, department.raw_department_id)

    @patch('auth.models.TeacherInformation.save',
           models.Model.save)
    @patch('auth.tasks.prod_logger')
    def test_update_from_teacher_information(self, mocked_prod_logger):
        '''Should update user from teacher information.'''
        num_departments = 10
        departments = [mommy.make(Department, id=idx)
                       for idx in range(1, 1 + num_departments)]
        dwid_to_department = {f'{dep.id}': dep for dep in departments}

        num_teachers = 20
        raw_users = [mommy.make(
            TeacherInformation, zgh=f'2{idx:02d}', jsxm=f'name{idx}',
            nl=f'{idx}', xb='1',
            xy=f'{idx % num_departments + 1 if idx != 1 else 100}',
            rxsj='2019-12-01', rzzt='11', xl='14', zyjszc='061', rjlx='12')
                     for idx in range(1, 1 + num_teachers)]

        _update_from_teacher_information(dwid_to_department)

        mocked_prod_logger.warning.assert_called_with(
            '职工号为201的教师使用了一个系统中不存在的学院100')

        users = User.objects.exclude(
            username='AnonymousUser').order_by('username')
        self.assertEqual(len(users), num_teachers)

        for raw_user, user in zip(raw_users, users):
            self.assertEqual(user.first_name, raw_user.jsxm)
            department = dwid_to_department.get(raw_user.xy)
            self.assertEqual(user.department_id,
                             department.id if department else None)
            self.assertEqual(
                user.gender,
                User.GENDER_CHOICES_MAP[raw_user.get_xb_display()])
            self.assertEqual(user.age, int(raw_user.nl))
            self.assertEqual(user.tenure_status, raw_user.get_rzzt_display())
            self.assertEqual(user.education_background,
                             raw_user.get_xl_display())
            self.assertEqual(user.technical_title,
                             raw_user.get_zyjszc_display())
            self.assertEqual(user.teaching_type, raw_user.get_rjlx_display())
