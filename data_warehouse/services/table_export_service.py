'''表格导出服务'''
import tempfile
import xlwt

from auth.models import Department
from infra.exceptions import BadRequest


class TableExportService:
    '''TableExportService'''
    COVERAGE_SHEET_NAME = '专任教师培训覆盖率'
    FEEDBACK_SHEET_NAME = '培训反馈表'
    TRAINING_HOURS_SHEET_NAME = '培训学时统计'

    @staticmethod
    def export_staff_basic_info():
        '''导出教职工表'''
        # TODO

    @staticmethod
    def export_teacher_basic_info(query_set):
        '''导出专任教师表'''
        # 初始化excel
        workbook = xlwt.Workbook()
        worksheet = workbook.add_sheet('专任教师情况汇总')
        style = xlwt.easyxf(('font: bold on; '
                             'align: wrap on, vert centre, horiz center'))
        # 生成表头
        worksheet.write_merge(0, 1, 0, 1, '项目', style)
        worksheet.write_merge(2, 2, 0, 1, '合计', style)
        worksheet.write_merge(0, 0, 2, 3, '专任教师', style)
        worksheet.write_merge(0, 0, 4, 5, '外聘教师', style)

        worksheet.write(1, 2, '数量', style)
        worksheet.write(1, 3, '比例（%）', style)
        worksheet.write(1, 4, '数量', style)
        worksheet.write(1, 5, '比例（%）', style)
        worksheet.write_merge(3,
                              3 + len(
                                  TableExportService.titles_zr.items()) - 1,
                              0, 0, '职称', style)
        # 专任教师--职称
        total_zr, rows_zr = TableExportService.__helper(query_set,
                                                        'teaching_type', 20,
                                                        'technical_title',
                                                        TableExportService
                                                        .titles_zr)
        ptr_r = 3
        ptr_c = 1
        TableExportService.__write(worksheet, ptr_r, ptr_c, total_zr, rows_zr,
                                   style)
        worksheet.write(2, 2, total_zr, style)
        worksheet.write(2, 3, 100, style)
        # 外聘教师--职称 TODO(WuJie) 什么是外聘教师
        total_wp, rows_wp = TableExportService.__helper(query_set,
                                                        'teaching_type', 21,
                                                        'technical_title',
                                                        TableExportService
                                                        .titles_zr)
        ptr_r = 3
        ptr_c = 4
        TableExportService.__write(worksheet, ptr_r, ptr_c, total_wp, rows_wp,
                                   style, False)
        worksheet.write(2, 4, total_wp, style)
        worksheet.write(2, 5, 100, style)
        # 专任教师--学位
        ptr_r += len(TableExportService.titles_zr.items())
        ptr_c = 1
        worksheet.write_merge(ptr_r,
                              ptr_r + len(
                                  TableExportService.education_zr.items()) - 1,
                              0, 0, '最高学位', style)
        total_zr, rows_zr = TableExportService.__helper(query_set,
                                                        'teaching_type', 20,
                                                        'education_background',
                                                        TableExportService
                                                        .education_zr)
        TableExportService.__write(worksheet, ptr_r, ptr_c, total_zr, rows_zr,
                                   style)
        # 外聘教师--学位
        ptr_c = 4
        total_wp, rows_wp = TableExportService.__helper(query_set,
                                                        'teaching_type', 21,
                                                        'education_background',
                                                        TableExportService
                                                        .education_zr)
        TableExportService.__write(worksheet, ptr_r, ptr_c, total_wp, rows_wp,
                                   style, False)

        # 专任教师--年龄
        ptr_r += len(TableExportService.education_zr.items())
        ptr_c = 1
        worksheet.write_merge(ptr_r, ptr_r + len(
            TableExportService.ages.items()) - 1,
                              0, 0, '年龄', style)
        total_zr, rows_zr = TableExportService.__helper(query_set,
                                                        'teaching_type', 20,
                                                        'age',
                                                        TableExportService
                                                        .ages,
                                                        mode='range')
        TableExportService.__write(worksheet, ptr_r, ptr_c, total_zr, rows_zr,
                                   style)
        # 外聘教师--年龄
        ptr_c = 4
        total_wp, rows_wp = TableExportService.__helper(query_set,
                                                        'teaching_type', 21,
                                                        'age',
                                                        TableExportService
                                                        .ages, mode='range')
        TableExportService.__write(worksheet, ptr_r, ptr_c, total_wp, rows_wp,
                                   style, False)

        # 写入数据
        _, file_path = tempfile.mkstemp()
        workbook.save(file_path)
        return file_path

    @staticmethod
    def export_training_summary():
        '''导出培训总体情况表'''
        # 初始化excel
        workbook = xlwt.Workbook()
        worksheet = workbook.add_sheet('培训总体情况汇总')
        style = xlwt.easyxf(('font: bold on; '
                             'align: wrap on, vert centre, horiz center'))
        # 生成表头
        worksheet.write_merge(0, 1, 0, 1, '类别', style)
        worksheet.write_merge(2, 2, 0, 1, '合计', style)
        worksheet.write_merge(0, 0, 2, 3, '专任教师', style)
        worksheet.write_merge(0, 0, 4, 5, '其他人员', style)

        worksheet.write(1, 2, '数量', style)
        worksheet.write(1, 3, '比例（%）', style)
        worksheet.write(1, 4, '数量', style)
        worksheet.write(1, 5, '比例（%）', style)
        # 单位数据
        departments_qs = Department.objects.all()
        worksheet.write_merge(3, 3 + len(departments_qs) - 1,
                              0, 0, '单位数据', style)
        deparment_filter_dict = {}
        for dept in departments_qs:
            deparment_filter_dict[dept.name] = dept.raw_department_id

        ptr = 3 + len(departments_qs)
        # 职称
        worksheet.write_merge(ptr, ptr + len(
            TableExportService.titles_trainning.items()) - 1,
                              0, 0, '职称', style)
        ptr += len(TableExportService.titles_trainning.items())
        # 年龄
        worksheet.write_merge(ptr, ptr + len(
            TableExportService.ages.items()) - 1,
                              0, 0, '年龄', style)

        # 写入数据
        _, file_path = tempfile.mkstemp()
        workbook.save(file_path)
        return file_path

    # pylint: disable=R0914
    @classmethod
    def export_traning_coverage_summary(cls, data):
        '''导出专任教师培训覆盖率表
        Parameters
        ------
        data: dict {
            'departments': list of dict {
                department: string, value: string,
                coverage_count: string, value: int,
                total_count: string, value: int
            }
            'ages': list of dict {
                age_range: string, value: string,
                coverage_count: string, value: int,
                total_count: string, value: int
            }
            'titles': list of dict {
                title: string, value: string,
                coverage_count: string, value: int,
                total_count: string, value: int

            }
        }

        Returns
        ------
        string
            导出的excel文件路径
        '''
        if data is None or not data.items():
            raise BadRequest('导出内容不存在。')
        # 初始化excel
        workbook = xlwt.Workbook()
        worksheet = workbook.add_sheet(cls.COVERAGE_SHEET_NAME)
        style = xlwt.easyxf(('font: bold on; '
                             'align: wrap on, vert centre, horiz center'))
        # 生成表头
        worksheet.write_merge(0, 0, 0, 1, '项目', style)
        worksheet.write(0, 2, '总人数', style)
        worksheet.write(0, 3, '参加培训人数', style)
        worksheet.write(0, 4, '覆盖率(%)', style)
        worksheet.write_merge(1, 1, 0, 1, '总计', style)
        # 各学部总人数合计
        total, coverage_total = 0, 0
        departments_data = data['departments']
        # we just keep a blank cell in case len(departments_data) is 0.
        worksheet.write_merge(2, max(2, 2 + len(departments_data) - 1),
                              0, 0, '单位数据', style)
        ptr_r = 2
        for summary in departments_data:
            worksheet.write(ptr_r, 1, summary['department'])
            worksheet.write(ptr_r, 2, summary['total_count'])
            worksheet.write(ptr_r, 3, summary['coverage_count'])
            worksheet.write(
                ptr_r, 4,
                0 if summary['total_count'] == 0 else summary['coverage_count']
                * 100 / summary['total_count']
                )
            total += summary['total_count']
            coverage_total += summary['coverage_count']
            ptr_r += 1
        if not departments_data:
            ptr_r += 1

        # 职称
        titles_data = data['titles']
        worksheet.write_merge(ptr_r, max(ptr_r, ptr_r + len(titles_data) - 1),
                              0, 0, '职称', style)
        for summary in titles_data:
            worksheet.write(ptr_r, 1, summary['title'])
            worksheet.write(ptr_r, 2, summary['total_count'])
            worksheet.write(ptr_r, 3, summary['coverage_count'])
            worksheet.write(
                ptr_r, 4,
                0 if summary['total_count'] == 0 else summary['coverage_count']
                * 100 / summary['total_count']
                )
            ptr_r += 1
        if not titles_data:
            ptr_r += 1

        # 年龄
        ages_data = data['ages']
        worksheet.write_merge(ptr_r, max(ptr_r, ptr_r + len(ages_data) - 1),
                              0, 0, '年龄', style)
        for summary in ages_data:
            worksheet.write(ptr_r, 1, summary['age_range'])
            worksheet.write(ptr_r, 2, summary['total_count'])
            worksheet.write(ptr_r, 3, summary['coverage_count'])
            worksheet.write(
                ptr_r, 4,
                0 if summary['total_count'] == 0 else summary['coverage_count']
                * 100 / summary['total_count']
                )
            ptr_r += 1

        if not ages_data:
            ptr_r += 1

        # 最后写合计
        worksheet.write(1, 2, total)
        worksheet.write(1, 3, coverage_total)
        worksheet.write(1, 4,
                        0 if total == 0 else coverage_total * 100 / total)

        # 写入数据
        _, file_path = tempfile.mkstemp()
        workbook.save(file_path)
        return file_path

    @staticmethod
    def export_training_hours(data):
        '''导出培训时长和工作量表
        Parameters
        ------
            data: list of dict {
                department,
                total_users,
                total_coveraged_users,
                total_hours
            }

        Returns
        ------
        string:
            excel file path.
        '''
        if not data:
            raise BadRequest('导出内容不存在。')
        # 初始化excel
        workbook = xlwt.Workbook()
        worksheet = workbook.add_sheet(
            TableExportService.TRAINING_HOURS_SHEET_NAME)
        style = xlwt.easyxf(('font: bold on; '
                             'align: wrap on, vert centre, horiz center'))
        # 生成表头
        worksheet.write(0, 0, '单位', style)
        worksheet.write(0, 1, '学院总人数', style)
        worksheet.write(0, 2, '覆盖总人数', style)
        worksheet.write(0, 3, '总培训学时', style)
        worksheet.write(0, 4, '人均培训学时（学院）', style)
        worksheet.write(0, 5, '人均培训学时（覆盖人群）', style)
        ptr_r = 1
        for item in data:
            worksheet.write(ptr_r, 0, item['department'])
            worksheet.write(ptr_r, 1, item['total_users'])
            worksheet.write(ptr_r, 2, item['total_coveraged_users'])
            worksheet.write(ptr_r, 3, item['total_hours'])
            worksheet.write(
                ptr_r, 4,
                '%.02f' % (
                    (item['total_hours']/item['total_users']) if
                    item['total_users'] > 0 else 0.0)
            )
            worksheet.write(
                ptr_r, 5,
                '%.02f' % (
                    (item['total_hours']/item['total_coveraged_users']) if
                    item['total_coveraged_users'] > 0 else 0.0)
            )
            ptr_r += 1

        # 写入数据
        _, file_path = tempfile.mkstemp()
        workbook.save(file_path)
        return file_path

    @classmethod
    def export_training_feedback(cls, data):
        '''导出培训反馈表
        Parameters
        ------

        data: list of dict {
            key: prgoram_name,
            key: campus_event_name,
            key: feedback_content,
            key: feedback_time,
            key: feedback_user_name,
            key: feedback_user_email
        }
        Returns
        -------
        string
            excel临时文件路径。
        '''
        if data is None or not data:
            raise BadRequest('导出内容不存在。')
        # 初始化excel
        workbook = xlwt.Workbook()
        worksheet = workbook.add_sheet(cls.FEEDBACK_SHEET_NAME)
        style = xlwt.easyxf(('font: bold on; '
                             'align: wrap on, vert centre, horiz center'))
        # 生成表头
        worksheet.write(0, 0, '培训项目', style)
        worksheet.write(0, 1, '培训活动', style)
        worksheet.write(0, 2, '反馈内容', style)
        worksheet.write(0, 3, '反馈时间', style)
        worksheet.write(0, 4, '反馈人姓名', style)
        worksheet.write(0, 5, '反馈人部门', style)
        worksheet.write(0, 6, '反馈人邮箱', style)

        ptr_r = 1
        for item in data:
            worksheet.write(ptr_r, 0, item['program_name'], style)
            worksheet.write(ptr_r, 1, item['campus_event_name'], style)
            worksheet.write(ptr_r, 2, item['feedback_content'], style)
            worksheet.write(ptr_r, 3, item['feedback_time'], style)
            worksheet.write(ptr_r, 4, item['feedback_user_name'], style)
            worksheet.write(ptr_r, 5, item['feedback_user_department'], style)
            worksheet.write(ptr_r, 6, item['feedback_user_email'], style)
            ptr_r += 1
        # 写入数据
        _, file_path = tempfile.mkstemp()
        workbook.save(file_path)
        return file_path
