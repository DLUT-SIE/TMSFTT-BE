'''Unit tests for canvas data formater services.'''
from django.test import TestCase
from model_mommy import mommy

from auth.models import Department
from data_warehouse.consts import EnumData
from data_warehouse.services.canvas_data_formater_service import (
    CanvasDataFormater
)


class TestCanvasDataFormaterService(TestCase):
    '''Test services provided by CanvasDataFormaterService.'''
    def setUp(self):
        self.department_dlut = mommy.make(
            Department, name='大连理工大学', id=1)
        top_department = mommy.make(
            Department, name='凌水主校区',
            super_department=self.department_dlut)
        self.department_art = mommy.make(
            Department, name='建筑与艺术学院', id=50,
            super_department=top_department,
            department_type='T3')
        self.department_sie = mommy.make(
            Department, name='创新创业学院', id=20,
            super_department=top_department,
            department_type='T3')

    def test_format_records_statistics_data(self):
        '''test format_records_statistics_data function'''
        group_records = {
            'campus_records': {},
            'off_campus_records': {}
        }
        group_records['campus_records'] = {'教授': 1}
        group_records['off_campus_records'] = {'教授': 2}
        data = CanvasDataFormater.format_records_statistics_data(
            group_records)
        self.assertIn(1, data['group_by_data'][0]['data'])
        self.assertIn(2, data['group_by_data'][1]['data'])
        self.assertEqual(data['label'], EnumData.TITLE_LABEL)
        group_records['campus_records'] = {'创院': 1}
        group_records['off_campus_records'] = {'创院': 2}
        data = CanvasDataFormater.format_records_statistics_data(
            group_records)
        self.assertEqual(data['group_by_data'][0]['data'], [1])
        self.assertEqual(data['group_by_data'][1]['data'], [2])
        self.assertEqual(data['label'], ['创院'])

    def test_format_teachers_statistics_data(self):
        '''test format_teachers_statistics_data function'''
        group_users = {}
        data = CanvasDataFormater.format_teachers_statistics_data(
            group_users
        )
        self.assertFalse(data['label'])
        group_users = {'教授': 1}
        data = CanvasDataFormater.format_teachers_statistics_data(
            group_users
        )
        self.assertEqual(data['label'], EnumData.TITLE_LABEL)
        self.assertIn(1, data['group_by_data'][0]['data'])
        group_users = {'创院': 1}
        data = CanvasDataFormater.format_teachers_statistics_data(
            group_users
        )
        self.assertEqual(data['label'], ['创院'])
        self.assertEqual(data['group_by_data'][0]['data'], [1])

    def test_format_coverage_statistics_data(self):
        '''test format_coverage_statistics_data function'''
        group_users = []
        data = CanvasDataFormater.format_coverage_statistics_data(
            group_users
        )
        self.assertFalse(data['label'])
        group_users = [{
            'age_range': '35岁及以下',
            'coverage_count': 1,
            'total_count': 1
        }]
        data = CanvasDataFormater.format_coverage_statistics_data(
            group_users
        )
        self.assertIn('35岁及以下', data['label'])
        group_users = [{
            'department': '创新创业学院',
            'coverage_count': 1,
            'total_count': 1
        }, {
            'department': '机械工程学院',
            'coverage_count': 1,
            'total_count': 1
        }]
        data = CanvasDataFormater.format_coverage_statistics_data(
            group_users
        )
        self.assertIn(1, data['group_by_data'][0]['data'])
        group_users = [{
            'title': '教授',
            'coverage_count': 1,
            'total_count': 1
        }, {
            'title': '未知',
            'coverage_count': 100,
            'total_count': 1
        }]
        data = CanvasDataFormater.format_coverage_statistics_data(
            group_users
        )
        self.assertIn('教授', data['label'])
        self.assertNotIn(100, data['group_by_data'][0]['data'])

    def test_format_hours_statistics_data(self):
        '''test format_hours_statistics_data function'''
        group_data = [{
            'department': '创新创业学院',
            'total_users': 10,
            'total_coveraged_users': 8,
            'total_hours': 10
        }, {
            'department': '机械工程学院',
            'total_users': 10,
            'total_coveraged_users': 8,
            'total_hours': 10
        }]
        data = CanvasDataFormater.format_hours_statistics_data(group_data)
        self.assertIn(group_data[0]['department'], data['label'])
        self.assertIn(1.25, data['group_by_data'][4]['data'])
