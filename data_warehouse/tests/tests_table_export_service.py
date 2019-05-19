'''表格导出服务模块测试'''
import xlrd
from django.test import TestCase
from data_warehouse.services.table_export_service import TableExportService
from infra.exceptions import BadRequest


class TestTableExportServices(TestCase):
    '''表格导出服务测试'''

    def setUp(self):
        self.mock_data = {
            'departments': [
                {
                    'department': '创新创业学院',
                    'coverage_count': 10,
                    'total_count': 20
                },
                {
                    'department': '计算机学院',
                    'coverage_count': 10,
                    'total_count': 20
                },
                {
                    'department': '机械学院',
                    'coverage_count': 10,
                    'total_count': 20
                },
                {
                    'department': '管理学院',
                    'coverage_count': 10,
                    'total_count': 20
                }],
            'titles': [
                {
                    'title': '教授',
                    'coverage_count': 10,
                    'total_count': 20
                },
                {
                    'title': '副教授',
                    'coverage_count': 10,
                    'total_count': 20
                },
                {
                    'title': '讲师',
                    'coverage_count': 10,
                    'total_count': 20
                },
                {
                    'title': '助教',
                    'coverage_count': 10,
                    'total_count': 20
                }],
            'ages': [
                {
                    'age_range': '35岁及以下',
                    'coverage_count': 10,
                    'total_count': 20
                },
                {
                    'age_range': '36-45岁',
                    'coverage_count': 10,
                    'total_count': 20
                },
                {
                    'age_range': '46-55岁',
                    'coverage_count': 10,
                    'total_count': 20
                },
                {
                    'age_range': '56岁及以上',
                    'coverage_count': 10,
                    'total_count': 20
                }]
            }

    def test_export_traning_coverage_summary_of_teacher(self):
        '''Should 创建正确的Excel文件'''
        file_path = TableExportService.export_traning_coverage_summary(
            self.mock_data)
        self.assertIsNotNone(file_path)
        workbook = xlrd.open_workbook(file_path)
        sheet = workbook.sheet_by_name(TableExportService.COVERAGE_SHEET_NAME)
        self.assertIsNotNone(sheet)
        self.assertEqual(
            sheet.cell_value(0, 0), '项目'
        )
        self.assertEqual(sheet.cell_value(0, 2), '总人数')
        self.assertEqual(sheet.cell_value(0, 3), '参加培训人数')
        self.assertEqual(sheet.cell_value(1, 0), '总计')
        self.assertEqual(sheet.cell_value(1, 2), 80.0)
        self.assertEqual(sheet.cell_value(1, 3), 40.0)
        self.assertEqual(sheet.cell_value(1, 4), 50.0)

        with self.assertRaisesMessage(BadRequest, '导出内容不存在。'):
            TableExportService.export_traning_coverage_summary({})

        self.mock_data['departments'] = []
        file_path = TableExportService.export_traning_coverage_summary(
            self.mock_data)
        self.assertIsNotNone(file_path)
        workbook = xlrd.open_workbook(file_path)
        sheet = workbook.sheet_by_name(TableExportService.COVERAGE_SHEET_NAME)
        self.assertIsNotNone(sheet)
        self.assertEqual(
            sheet.cell_value(0, 0), '项目'
        )
        self.assertEqual(sheet.cell_value(0, 2), '总人数')
        self.assertEqual(sheet.cell_value(0, 3), '参加培训人数')
        self.assertEqual(sheet.cell_value(1, 0), '总计')
        self.assertEqual(sheet.cell_value(1, 2), 0.0)
        self.assertEqual(sheet.cell_value(1, 3), 0.0)
        self.assertEqual(sheet.cell_value(1, 4), 0.0)
        self.assertEqual(sheet.cell_value(2, 0), '单位数据')
        self.assertEqual(sheet.cell_value(2, 1), '')
