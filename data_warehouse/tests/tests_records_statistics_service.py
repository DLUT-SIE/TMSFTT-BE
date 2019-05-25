'''Unit tests for records statistics services.'''
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.http import HttpRequest
from django.utils.timezone import now
from django.contrib.auth.models import Group
from model_mommy import mommy

from auth.models import Department
from data_warehouse.services.records_statistics_service import (
    RecordsStatisticsService
)
from infra.exceptions import BadRequest
from training_event.models import CampusEvent
from training_record.models import Record


User = get_user_model()


class TestRecordsStatisticsService(TestCase):
    '''Test services provided by RecordsStatisticsService.'''
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
            age=40,
            teaching_type='专任教师')
        self.user.groups.add(self.dlut_group)
        self.request = HttpRequest()
        self.request.user = self.user
        self.campus_event = mommy.make(CampusEvent, time=now())
        self.record = mommy.make(
            Record, user=self.user, campus_event=self.campus_event)

    def test_records_statistics_group_dispatch(self):
        '''test records_statistics_group_dispatch function'''
        records = Record.objects.none()
        with self.assertRaisesMessage(BadRequest, '错误的参数'):
            RecordsStatisticsService.records_statistics_group_dispatch(
                records, 100, True)
        data = RecordsStatisticsService.records_statistics_group_dispatch(
            records, 1, True)
        self.assertIn('教授', data)

    def test_group_records_by_technical_title(self):
        '''test group_records_by_technical_title function'''
        records = Record.objects.all()
        group_records = (
            RecordsStatisticsService.group_records_by_technical_title(
                records, True))
        self.assertEqual(group_records['教授'], 1)
        group_records = (
            RecordsStatisticsService.group_records_by_technical_title(
                records, False))
        self.assertEqual(list(group_records['教授']), [self.record])

    def test_group_records_by_department(self):
        '''test group_records_by_department function'''
        records = Record.objects.all()
        group_records = (
            RecordsStatisticsService.group_records_by_department(
                records, True))
        self.assertEqual(group_records['建筑与艺术学院'], 1)
        group_records = (
            RecordsStatisticsService.group_records_by_department(
                records, False))
        self.assertEqual(list(group_records['建筑与艺术学院']), [self.record])

    def test_group_records_by_age(self):
        '''test group_records_by_age function'''
        records = Record.objects.all()
        group_records = (
            RecordsStatisticsService.group_records_by_age(
                records, True))
        self.assertEqual(group_records['36-45岁'], 1)
        group_records = (
            RecordsStatisticsService.group_records_by_age(
                records, False))
        self.assertEqual(list(group_records['36-45岁']), [self.record])

    def test_get_records_by_time_department(self):
        '''test get_records_by_time_department function'''
        time = {
            'start': 2020,
            'end': 2019
        }
        art_group = mommy.make(Group, name='建筑与艺术学院-管理员')
        art_user = mommy.make(User)
        art_user.groups.add(art_group)
        with self.assertRaisesMessage(BadRequest, '错误的参数'):
            RecordsStatisticsService.get_records_by_time_department(
                self.user, self.department_art.id, time)
        records = RecordsStatisticsService.get_records_by_time_department(
            self.user, 0, None)
        self.assertFalse(records['campus_records'])
        records = RecordsStatisticsService.get_records_by_time_department(
            self.user, self.department_dlut.id, None)
        self.assertIn(self.record, records['campus_records'])
        records = RecordsStatisticsService.get_records_by_time_department(
            self.user, self.department_art.id, None)
        self.assertIn(self.record, records['campus_records'])
        records = RecordsStatisticsService.get_records_by_time_department(
            art_user, self.department_art.id, None)
        self.assertIn(self.record, records['campus_records'])
