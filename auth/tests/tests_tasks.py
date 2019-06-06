'''Unit tests for Celery tasks.'''
from datetime import datetime
from unittest.mock import patch, Mock

from django.test import TestCase
from django.db import models
from django.contrib.auth.models import Group
from django.utils.timezone import now, make_aware
from model_mommy import mommy

from auth.models import (
    User, Department, DepartmentInformation, TeacherInformation)
from auth.tasks import (
    _update_from_department_information,
    _update_from_teacher_information,
    update_teachers_and_departments_information
)


class TestUpdateTeachersAndDepartmentsInformation(TestCase):
    '''Unit tests for syncing from provided data.'''

    @classmethod
    def setUpTestData(cls):
        cls.dlut_name = '大连理工大学'
        cls.dlut_id = '10141'
        cls.num_departments = 10
        cls.num_teachers = 10
        cls.dlut = Department.objects.create(raw_department_id=cls.dlut_id,
                                             name=cls.dlut_name)
        cls.dlut_set = set()
        cls.dlut_group = Group.objects.create(name=f'{cls.dlut_name}-专任教师')
        cls.dlut_set.add(cls.dlut_group)

    @patch('auth.tasks.prod_logger')
    @patch('auth.tasks._update_from_department_information')
    @patch('auth.tasks._update_from_teacher_information')
    def test_call_update_functions(
            self, mocked_teacher_update_func, mocked_department_update_func,
            mocked_prod_logger):
        '''Should call update functions.'''
        dwid_to_department = Mock()
        department_id_to_administrative = Mock()
        mocked_department_update_func.return_value = (
            dwid_to_department, department_id_to_administrative)

        update_teachers_and_departments_information()

        mocked_department_update_func.assert_called()
        mocked_teacher_update_func.assert_called_with(
            dwid_to_department, department_id_to_administrative)
        mocked_prod_logger.exception.assert_not_called()

    @patch('auth.tasks.Group.objects.get_or_create')
    @patch('auth.tasks.prod_logger')
    @patch('auth.models.DepartmentInformation.save', models.Model.save)
    def test_logging_if_department_update_failed(
            self, mocked_prod_logger, mocked_get_or_create):
        '''Should call update functions.'''
        depart = DepartmentInformation.objects.create(dwid='123', dwmc='123')
        exc = Exception('Oops')
        mocked_get_or_create.side_effect = exc
        with self.assertRaises(Exception):
            _update_from_department_information()

        mocked_prod_logger.exception.assert_called_with(
            '部门信息更新失败,单位号:%s, excepiton:%s', depart.dwid, exc)

    @patch('auth.tasks.User.all_objects.get_or_create')
    @patch('auth.tasks.prod_logger')
    @patch('auth.models.TeacherInformation.save', models.Model.save)
    def test_logging_if_teacher_update_failed(
            self, mocked_prod_logger, mocked_get_or_create):
        '''Should call update functions.'''
        exc = Exception('Oops')
        mocked_get_or_create.side_effect = exc
        user = TeacherInformation.objects.create(zgh='123')
        departments = [mommy.make(
            Department, raw_department_id=idx,
            name=f'Department{idx}') for idx in range(1, 5)]
        with self.assertRaises(Exception):
            _update_from_teacher_information(
                {f'{departments[0].id}': departments[0]}, {1: departments[1]})
        mocked_prod_logger.exception.assert_called_with(
            '用户信息更新失败,职工号:%s, exception:%s', user.zgh, exc)

    @patch('auth.models.DepartmentInformation.save',
           models.Model.save)
    @patch('auth.tasks.prod_logger')
    def test_update_from_department_information(self, _):
        '''Should update department from department information.'''
        mommy.make(DepartmentInformation,
                   dwid=self.dlut_id, dwmc=self.dlut_name)
        infos = [mommy.make(DepartmentInformation,
                            dwid=f'{idx}',
                            dwmc=f'Department{idx}',
                            lsdw=1,
                            _fill_optional=True,
                            dwlx=Department.DEPARTMENT_TYPE_T1
                            )
                 for idx in range(self.num_departments)]
        dwid_to_department, department_id_to_administrative = (
            _update_from_department_information()
        )
        departments = Department.objects.exclude(
            raw_department_id=self.dlut_id).order_by('raw_department_id')
        self.assertEqual(len(departments), self.num_departments)
        self.assertEqual(len(dwid_to_department), self.num_departments)

        self.assertEqual(len(department_id_to_administrative),
                         self.num_departments)

        for info, department in zip(infos, departments):
            if info.dwmc == self.dlut_name:
                continue
            self.assertEqual(info.dwmc, department.name)
            self.assertEqual(info.dwid, department.raw_department_id)

    @patch('auth.models.TeacherInformation.save',
           models.Model.save)
    @patch('auth.tasks.prod_logger')
    def test_update_from_teacher_information(self, _):
        '''Should update user from teacher information.'''
        # pylint: disable=too-many-locals

        departments = [mommy.make(
            Department, id=idx, raw_department_id=idx,
            name=f'Department{idx}') for idx in range(1,
                                                      1 +
                                                      self.num_departments)]
        for department in departments:
            department.super_department = self.dlut
            group_names = [f'{department.name}-管理员',
                           f'{department.name}-专任教师']
            for group_name in group_names:
                Group.objects.get_or_create(name=group_name)
            department.save()
        departments[0].super_department = departments[1]
        departments[1].super_department = departments[2]
        departments[0].save()
        departments[1].save()
        groups_set = set()
        for idx in range(3):
            groups_set.add(
                Group.objects.get(name=f'{departments[idx].name}-专任教师'))
        # 由于map是手动生成，mock时保证map中的链路在department自连接中存在
        department_id_to_administrative = {
            dep.id: departments[dep.id - 1] for dep in departments}
        department_id_to_administrative[departments[0].id] = departments[2]
        department_id_to_administrative[departments[1].id] = departments[2]

        dwid_to_department = {f'{dep.id}': dep for dep in departments}
        csrq = '1980-01-01'
        birthday = make_aware(datetime.strptime(csrq, '%Y-%m-%d'))
        age = (now() - birthday).days // 365
        raw_users = [mommy.make(
            TeacherInformation, zgh=f'2{idx:02d}', jsxm=f'name{idx}',
            csrq=csrq, xb='1', yxdz='asdf@123.com',
            xy=f'{departments[idx - 1].raw_department_id}',
            rxsj='2019-12-01', rzzt='11', xl='14', zyjszc='061', rjlx='12')
                     for idx in range(1, 1 + self.num_teachers)]
        _update_from_teacher_information(dwid_to_department,
                                         department_id_to_administrative)
        users = User.objects.exclude(
            username='AnonymousUser').order_by('username')
        self.assertEqual(len(users), self.num_teachers)

        groups = users[0].groups.all()
        self.assertEqual(set(groups) - self.dlut_set, groups_set)

        for raw_user, user in zip(raw_users, users):
            self.assertEqual(user.first_name, raw_user.jsxm)
            department = dwid_to_department.get(raw_user.xy)
            self.assertEqual(user.department_id,
                             department.id if department else None)
            self.assertEqual(
                user.gender,
                User.GENDER_CHOICES_MAP[raw_user.get_xb_display()])
            self.assertEqual(user.age, age)
            self.assertEqual(user.tenure_status, raw_user.get_rzzt_display())
            self.assertEqual(user.education_background,
                             raw_user.get_xl_display())
            self.assertEqual(user.technical_title,
                             raw_user.get_zyjszc_display())
            self.assertEqual(user.teaching_type, raw_user.get_rjlx_display())
