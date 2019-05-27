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

    def test_export_traning_feedback(self):
        '''Should 正确的导出培训反馈'''
        mock_data = []
        with self.assertRaisesMessage(BadRequest, '导出内容不存在。'):
            TableExportService.export_training_feedback(mock_data)

        mock_data = [
            {
                'program_name': 'test_program',
                'campus_event_name': 'test_event',
                'feedback_content': 'test_feedback_content',
                'feedback_time': '2018-01-01 12:42',
                'feedback_user_name': 'test_user',
                'feedback_user_department': 'test_department',
                'feedback_user_email': 'exmaple@test.com'
            }
        ]
        file_path = TableExportService.export_training_feedback(mock_data)
        self.assertIsNotNone(file_path)
        workbook = xlrd.open_workbook(file_path)
        sheet = workbook.sheet_by_name(TableExportService.FEEDBACK_SHEET_NAME)
        self.assertIsNotNone(sheet)
        self.assertEqual(sheet.cell_value(0, 0), '培训项目')
        self.assertEqual(sheet.cell_value(0, 1), '培训活动')
        self.assertEqual(sheet.cell_value(0, 2), '反馈内容')
        self.assertEqual(sheet.cell_value(0, 3), '反馈时间')
        self.assertEqual(sheet.cell_value(0, 4), '反馈人姓名')
        self.assertEqual(sheet.cell_value(0, 5), '反馈人部门')
        self.assertEqual(sheet.cell_value(0, 6), '反馈人邮箱')
        self.assertEqual(sheet.cell_value(1, 0), 'test_program')
        self.assertEqual(sheet.cell_value(1, 1), 'test_event')
        self.assertEqual(sheet.cell_value(1, 2), 'test_feedback_content')
        self.assertEqual(sheet.cell_value(1, 3), '2018-01-01 12:42')
        self.assertEqual(sheet.cell_value(1, 4), 'test_user')
        self.assertEqual(sheet.cell_value(1, 5), 'test_department')
        self.assertEqual(sheet.cell_value(1, 6), 'exmaple@test.com')

    def test_export_training_hours(self):
        '''Should 正确的导出培训学时与工作量表'''
        mock_data = []
        with self.assertRaisesMessage(BadRequest, '导出内容不存在。'):
            TableExportService.export_training_hours(mock_data)

        mock_data = [
            {
                'department': 'test_department',
                'total_users': 10,
                'total_coveraged_users': 9,
                'total_hours': 100
            }
        ]
        file_path = TableExportService.export_training_hours(mock_data)
        self.assertIsNotNone(file_path)
        workbook = xlrd.open_workbook(file_path)
        sheet = workbook.sheet_by_name(
            TableExportService.TRAINING_HOURS_SHEET_NAME)
        self.assertIsNotNone(sheet)
        self.assertEqual(sheet.cell_value(0, 0), '单位')
        self.assertEqual(sheet.cell_value(0, 1), '学院总人数')
        self.assertEqual(sheet.cell_value(0, 2), '覆盖总人数')
        self.assertEqual(sheet.cell_value(0, 3), '总培训学时')
        self.assertEqual(sheet.cell_value(0, 4), '人均培训学时（学院）')
        self.assertEqual(sheet.cell_value(0, 5), '人均培训学时（覆盖人群）')

        self.assertEqual(sheet.cell_value(1, 0), 'test_department')
        self.assertEqual(sheet.cell_value(1, 1), 10)
        self.assertEqual(sheet.cell_value(1, 2), 9)
        self.assertEqual(sheet.cell_value(1, 3), 100)
        self.assertEqual(sheet.cell_value(1, 4), '%.2f' % (100 / 10))
        self.assertEqual(sheet.cell_value(1, 5), '%.2f' % (100 / 9))
