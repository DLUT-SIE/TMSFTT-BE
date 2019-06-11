'''表格导出服务模块测试'''
import xlrd
from django.test import TestCase
from django.utils.timezone import datetime
from model_mommy import mommy
from data_warehouse.services.table_export_service import TableExportService
from infra.exceptions import BadRequest
from auth.models import User, Department
from training_event.models import (
    CampusEvent, Enrollment
)


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
        self.assertEqual(sheet.cell_value(1, 4), '50.00')

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
        self.assertEqual(sheet.cell_value(1, 4), '0.00')
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

    def test_export_records_for_user(self):
        '''Should export matched records'''
        mock_data = [
            {
                'event_name': 'event_name',
                'event_time': datetime.strptime('2013-09-02', '%Y-%m-%d'),
                'event_location': 'event_location',
                'num_hours': '2',
                'create_time': datetime.strptime('2014-08-23', '%Y-%m-%d'),
                'role': 1,
                'status': 2,
            }
        ]
        file_path = TableExportService.export_records_for_user(mock_data)
        self.assertIsNotNone(file_path)
        workbook = xlrd.open_workbook(file_path)
        sheet = workbook.sheet_by_name(TableExportService.RECORD_SHEET_NAME)
        self.assertIsNotNone(sheet)
        self.assertEqual(sheet.cell_value(0, 0), '培训项目')
        self.assertEqual(sheet.cell_value(0, 1), '时间')
        self.assertEqual(sheet.cell_value(0, 2), '地点')
        self.assertEqual(sheet.cell_value(0, 3), '学时')
        self.assertEqual(sheet.cell_value(0, 4), '参与身份')
        self.assertEqual(sheet.cell_value(0, 5), '创建时间')
        self.assertEqual(sheet.cell_value(0, 6), '审核状态')
        self.assertEqual(sheet.cell_value(1, 0), 'event_name')
        self.assertEqual(sheet.cell_value(1, 1), '2013-09-02')
        self.assertEqual(sheet.cell_value(1, 2), 'event_location')
        self.assertEqual(sheet.cell_value(1, 3), '2')
        self.assertEqual(sheet.cell_value(1, 4), 1)
        self.assertEqual(sheet.cell_value(1, 5), '2014-08-23')
        self.assertEqual(sheet.cell_value(1, 6), 2)

    def test_export_teacher_statistics(self):
        '''Should 正确的导出专任教师表'''
        mock_data = [
            {
                '测试学院1': 12,
                '测试学院2': 15,
                '测试学院3': 13
            },
            {
                '教授': 10,
                '副教授': 12,
                '讲师': 18
            },
            {
                '博士研究所学历': 10,
                '硕士研究生学历': 10,
                '本科学士学历': 10,
                '大专学历': 10
            },
            {
                '35岁以下': 40
            }]

        file_path = TableExportService.export_teacher_statistics(mock_data)
        self.assertIsNotNone(file_path)
        workbook = xlrd.open_workbook(file_path)
        sheet = workbook.sheet_by_name(TableExportService.TEACHER_SHEET_NAME)
        self.assertIsNotNone(sheet)

        self.assertEqual(sheet.cell_value(0, 0), '项目')
        self.assertEqual(sheet.cell_value(2, 0), '总计')
        self.assertEqual(sheet.cell_value(0, 2), '专任教师')
        self.assertEqual(sheet.cell_value(1, 2), '数量')
        self.assertEqual(sheet.cell_value(1, 3), '比例（%）')

        self.assertEqual(sheet.cell_value(2, 2), 40.0)
        self.assertEqual(sheet.cell_value(2, 3), '100.00')

        self.assertEqual(sheet.cell_value(3, 0), '院系')
        self.assertEqual(sheet.cell_value(6, 0), '职称')
        self.assertEqual(sheet.cell_value(9, 0), '年龄')
        self.assertEqual(sheet.cell_value(13, 0), '最高学位')

    def test_export_training_summary(self):
        '''Should 正确的导出培训总体情况表'''
        mock_data = [
            {
                'campus_records':
                {
                    '测试学院1': 12,
                    '测试学院2': 15,
                    '测试学院3': 13
                },
                'off_campus_records':
                {
                    '测试学院1': 12,
                    '测试学院2': 15,
                    '测试学院3': 13
                }
            },
            {
                'campus_records':
                {
                    '教授': 10,
                    '副教授': 12,
                    '讲师': 18
                },
                'off_campus_records':
                {
                    '教授': 10,
                    '副教授': 12,
                    '讲师': 18
                },
            },
            {
                'campus_records':
                {
                    '35岁以下': 40
                },
                'off_campus_records':
                {
                    '35岁以下': 40
                }
            }
            ]

        file_path = TableExportService.export_training_summary(mock_data)
        self.assertIsNotNone(file_path)
        workbook = xlrd.open_workbook(file_path)
        sheet = workbook.sheet_by_name(
            TableExportService.TEACHER_SUMMARY_SHEET_NAME)
        self.assertIsNotNone(sheet)

        self.assertEqual(sheet.cell_value(0, 0), '类别')
        self.assertEqual(sheet.cell_value(2, 0), '总计')
        self.assertEqual(sheet.cell_value(0, 2), '校内培训')
        self.assertEqual(sheet.cell_value(0, 4), '校外培训')
        self.assertEqual(sheet.cell_value(1, 2), '数量')
        self.assertEqual(sheet.cell_value(1, 3), '比例（%）')
        self.assertEqual(sheet.cell_value(1, 4), '数量')
        self.assertEqual(sheet.cell_value(1, 5), '比例（%）')

        self.assertEqual(sheet.cell_value(2, 2), 40.0)
        self.assertEqual(sheet.cell_value(2, 4), 40.0)
        self.assertEqual(sheet.cell_value(2, 3), '100.00')
        self.assertEqual(sheet.cell_value(2, 5), '100.00')

        self.assertEqual(sheet.cell_value(3, 0), '院系')
        self.assertEqual(sheet.cell_value(6, 0), '职称')
        self.assertEqual(sheet.cell_value(9, 0), '年龄')

    def test_export_attendance_sheet(self):
        '''Should export attendance sheet'''
        mock_data = []
        with self.assertRaisesMessage(BadRequest, '导出内容不存在。'):
            TableExportService.export_attendance_sheet(mock_data)

        event = mommy.make(CampusEvent, id=1, num_participants=10)
        department = mommy.make(
            Department, name='大连理工大学', id=1)
        user = mommy.make(User,
                          department=department,
                          username='201581108',
                          first_name='event',
                          last_name='event',
                          email='a@a.com',
                          cell_phone_number='123456789',
                          technical_title='教授'
                          )
        mock_data = [mommy.make(Enrollment, user=user, campus_event=event)]

        file_path = TableExportService.export_attendance_sheet(mock_data)
        self.assertIsNotNone(file_path)
        workbook = xlrd.open_workbook(file_path)
        sheet = workbook.sheet_by_name(
            TableExportService.ATTENDANCE_SHEET_NAME)
        self.assertIsNotNone(sheet)
        self.assertEqual(sheet.cell_value(2, 0), '序号')
        self.assertEqual(sheet.cell_value(2, 1), '院系')
        self.assertEqual(sheet.cell_value(2, 2), '工号')
        self.assertEqual(sheet.cell_value(2, 3), '姓名')
        self.assertEqual(sheet.cell_value(2, 4), '电话')
        self.assertEqual(sheet.cell_value(2, 5), '邮箱')
        self.assertEqual(sheet.cell_value(2, 6), '职称')
        self.assertEqual(sheet.cell_value(2, 7), '参与形式')
        self.assertEqual(sheet.cell_value(2, 8), '签到')
        self.assertEqual(sheet.cell_value(3, 0), 1)
        self.assertEqual(sheet.cell_value(3, 1), '大连理工大学')
        self.assertEqual(sheet.cell_value(3, 2), '201581108')
        self.assertEqual(sheet.cell_value(3, 3), 'eventevent')
        self.assertEqual(sheet.cell_value(3, 4), '123456789')
        self.assertEqual(sheet.cell_value(3, 5), 'a@a.com')
        self.assertEqual(sheet.cell_value(3, 6), '教授')
