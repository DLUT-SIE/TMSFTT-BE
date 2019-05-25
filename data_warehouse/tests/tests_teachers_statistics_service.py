'''Unit tests for teachers statistics services.'''
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.http import HttpRequest
from django.utils.timezone import now
from django.contrib.auth.models import Group
from model_mommy import mommy

from auth.models import Department
from data_warehouse.services.teachers_statistics_service import (
    TeachersStatisticsService
)
from infra.exceptions import BadRequest


User = get_user_model()


class TestTeachersStatisticsService(TestCase):
    '''Test services provided by TeachersStatisticsService.'''
    def setUp(self):
        self.dlut_group = mommy.make(Group, name="大连理工大学-管理员")
        self.department_dlut = mommy.make(
            Department, name='大连理工大学', id=1,
            create_time=now(), update_time=now())
        top_department = mommy.make(
            Department, name='凌水主校区',
            super_department=self.department_dlut,
            create_time=now(), update_time=now())
        self.department_art = mommy.make(
            Department, name='建筑与艺术学院', id=50,
            super_department=top_department,
            department_type='T3',
            create_time=now(), update_time=now())
        self.user = mommy.make(
            User,
            technical_title='教授',
            administrative_department=self.department_art,
            education_background='研究生毕业',
            age=40,
            teaching_type='专任教师')
        self.user.groups.add(self.dlut_group)
        self.request = HttpRequest()
        self.request.user = self.user

    def test_teachers_statistics_group_dispatch(self):
        '''test teachers_statistics_group_dispatch function'''
        users = User.objects.all()
        with self.assertRaisesMessage(BadRequest, '错误的参数'):
            TeachersStatisticsService.teachers_statistics_group_dispatch(
                users, 100, True)
        data = TeachersStatisticsService.teachers_statistics_group_dispatch(
            users, 1, True)
        self.assertIn('教授', data)

    def test_group_users_by_technical_title(self):
        '''test group_users_by_technical_title function'''
        users = User.objects.all()
        group_users = (
            TeachersStatisticsService.group_users_by_technical_title(
                users, True))
        self.assertEqual(group_users['教授'], 1)
        group_users = (
            TeachersStatisticsService.group_users_by_technical_title(
                users, False))
        self.assertEqual(list(group_users['教授']), [self.user])

    def test_group_users_by_education_background(self):
        '''test group_users_by_education_background function'''
        users = User.objects.all()
        group_users = (
            TeachersStatisticsService.group_users_by_education_background(
                users, True))
        self.assertEqual(group_users['研究生毕业'], 1)
        group_users = (
            TeachersStatisticsService.group_users_by_education_background(
                users, False))
        self.assertEqual(list(group_users['研究生毕业']), [self.user])

    def test_group_users_by_department(self):
        '''test group_users_by_department function'''
        users = User.objects.all()
        group_users = (
            TeachersStatisticsService.group_users_by_department(
                users, True))
        self.assertEqual(group_users['建筑与艺术学院'], 1)
        group_users = (
            TeachersStatisticsService.group_users_by_department(
                users, False))
        self.assertEqual(list(group_users['建筑与艺术学院']), [self.user])

    def test_group_users_by_age(self):
        '''test group_users_by_age function'''
        users = User.objects.all()
        group_users = (
            TeachersStatisticsService.group_users_by_age(
                users, True))
        self.assertEqual(group_users['36-45岁'], 1)
        group_users = (
            TeachersStatisticsService.group_users_by_age(
                users, False))
        self.assertEqual(list(group_users['36-45岁']), [self.user])

    def test_get_users_by_department(self):
        '''test get_users_by_department function'''
        art_group = mommy.make(Group, name='建筑与艺术学院-管理员')
        art_user = mommy.make(User)
        art_user.groups.add(art_group)
        users = TeachersStatisticsService.get_users_by_department(
            self.user, 0
        )
        self.assertFalse(users)
        users = TeachersStatisticsService.get_users_by_department(
            self.user, self.department_dlut.id
        )
        self.assertIn(self.user, list(users))
        users = TeachersStatisticsService.get_users_by_department(
            self.user, self.department_art.id
        )
        self.assertIn(self.user, list(users))
        users = TeachersStatisticsService.get_users_by_department(
            art_user, self.department_art.id
        )
        self.assertIn(self.user, list(users))
        users = TeachersStatisticsService.get_users_by_department(
            art_user, self.department_dlut.id
        )
        self.assertFalse(users)
