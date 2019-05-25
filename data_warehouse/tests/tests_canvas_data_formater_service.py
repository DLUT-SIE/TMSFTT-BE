'''Unit tests for canvas data formater services.'''
from django.test import TestCase

from data_warehouse.consts import EnumData
from data_warehouse.services.canvas_data_formater_service import (
    CanvasDataFormater
)


class TestCanvasDataFormaterService(TestCase):
    '''Test services provided by CanvasDataFormaterService.'''

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
        self.assertEqual(data['label'], ['35岁及以下'])
        group_users = [{
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
        self.assertEqual(data['label'], ['教授'])
        self.assertNotIn(100, data['group_by_data'][0]['data'])
