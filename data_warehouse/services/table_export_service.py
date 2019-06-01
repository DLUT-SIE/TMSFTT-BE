'''表格导出服务'''
import tempfile
from django.utils.timezone import now
import xlwt
from infra.exceptions import BadRequest


class TableExportService:
    '''TableExportService'''
    COVERAGE_SHEET_NAME = '专任教师培训覆盖率'
    FEEDBACK_SHEET_NAME = '培训反馈表'
    TRAINING_HOURS_SHEET_NAME = '培训学时统计'
    RECORD_SHEET_NAME = '个人培训记录'
    TEACHER_SHEET_NAME = '专任教师情况汇总'
    TEACHER_SUMMARY_SHEET_NAME = '培训总体情况汇总'
    ATTENDANCE_SHEET_NAME = '签到表'

    # pylint: disable=R0914
    @staticmethod
    def export_teacher_statistics(data):
        '''导出专任教师表
        Parameters
        -------
        data: list of dict {
            key: string
                分组后的标签名，例如按学院分组时则为学院的名称。
            value: int
                人数
        }
            data[0] 按部门分组数据，data[1]按职称分组数据
            data[2] 按年龄分组数据， data[3]按最高学位分组数据
        Returns
        -------
        str:
            excel file path.
        '''
        # 初始化excel
        workbook = xlwt.Workbook()
        worksheet = workbook.add_sheet(TableExportService.TEACHER_SHEET_NAME)
        style = xlwt.easyxf(('font: bold on; '
                             'align: wrap on, vert centre, horiz center'))
        # 生成表头
        worksheet.write_merge(0, 1, 0, 1, '项目', style)
        worksheet.write_merge(2, 2, 0, 1, '总计', style)
        worksheet.write_merge(0, 0, 2, 3, '专任教师', style)
        worksheet.write(1, 2, '数量', style)
        worksheet.write(1, 3, '比例（%）', style)

        # 分组
        groupby_labels = ('院系', '职称', '年龄', '最高学位')
        ptr_r = 3
        total = 0
        for idx, data_item in enumerate(data):
            total = sum(data_item.values())
            for key, value in data_item.items():
                worksheet.write(ptr_r, 1, key)
                worksheet.write(ptr_r, 2, value)
                percent = 0.0 if total == 0 else value * 100 / total
                worksheet.write(ptr_r, 3, f'{percent:.2f}')
                ptr_r += 1
            # we ensure top always is bigger than down in case
            # data is empty.
            top = min(ptr_r - len(data_item), ptr_r - 1)
            down = max(ptr_r - len(data_item), ptr_r - 1)
            worksheet.write_merge(top, down, 0, 0, groupby_labels[idx], style)
        # 写入合计
        worksheet.write(2, 2, total)
        worksheet.write(2, 3, f'{100:.2f}')
        TableExportService.__write_timestamp(worksheet, ptr_r, 0)
        _, file_path = tempfile.mkstemp()
        workbook.save(file_path)
        return file_path

    @staticmethod
    def export_training_summary(data):
        '''导出培训总体情况表（含校内和校外培训活动）
        Parameters
        -------
        data: list of dict {
            campus_records: dict {
                key: string
                    分组后的标签名，例如按学院分组时则为学院的名称。
                value: int
                    人数
            },
                校内培训活动
            off_campus_records: dict {
               key: string
                    分组后的标签名，例如按学院分组时则为学院的名称。
                value: int
                    人数
            }
                校外培训活动
        }
            data[0] 按部门分组数据，data[1]按职称分组数据
            data[2] 按年龄分组数据。

        Returns
        -------
        str:
            excel file path.
        '''
        # 初始化excel
        workbook = xlwt.Workbook()
        worksheet = workbook.add_sheet(
            TableExportService.TEACHER_SUMMARY_SHEET_NAME)
        style = xlwt.easyxf(('font: bold on; '
                             'align: wrap on, vert centre, horiz center'))
        # 生成表头
        worksheet.write_merge(0, 1, 0, 1, '类别', style)
        worksheet.write_merge(2, 2, 0, 1, '总计', style)
        worksheet.write_merge(0, 0, 2, 3, '校内培训', style)
        worksheet.write_merge(0, 0, 4, 5, '校外培训', style)

        worksheet.write(1, 2, '数量', style)
        worksheet.write(1, 3, '比例（%）', style)
        worksheet.write(1, 4, '数量', style)
        worksheet.write(1, 5, '比例（%）', style)

        # 分组
        groupby_labels = ('院系', '职称', '年龄')
        ptr_r = 3
        total_campus, total_off_campus = 0, 0
        # iterate different group bys.
        for idx, data_item in enumerate(data):
            total_campus = sum(data_item['campus_records'].values())
            total_off_campus = sum(data_item['off_campus_records'].values())
            # iterate campus_records and off_campus_records
            zipped_data = []
            for key, value in data_item['campus_records'].items():
                zipped_data.append(
                    (key, value, data_item['off_campus_records'][key])
                    )
            for dept, campus_cnt, off_campus_cnt in zipped_data:
                worksheet.write(ptr_r, 1, dept)
                worksheet.write(ptr_r, 2, campus_cnt)
                percent = 0.0 if total_campus == 0 else (
                    campus_cnt * 100 / total_campus)
                worksheet.write(ptr_r, 3, f'{percent:.2f}')
                worksheet.write(ptr_r, 4, off_campus_cnt)
                percent = 0.0 if total_off_campus == 0 else (
                    off_campus_cnt * 100 / total_off_campus)
                worksheet.write(ptr_r, 5, f'{percent:.2f}')
                ptr_r += 1
            # we ensure top always is bigger than down in case
            # data is empty.
            top = min(ptr_r - len(data_item['campus_records']), ptr_r - 1)
            down = max(ptr_r - len(data_item['campus_records']), ptr_r - 1)
            worksheet.write_merge(top, down, 0, 0, groupby_labels[idx], style)
        # 写入合计
        worksheet.write(2, 2, total_campus)
        worksheet.write(2, 4, total_off_campus)
        worksheet.write(2, 3, f'{100:.2f}')
        worksheet.write(2, 5, f'{100:.2f}')

        # 写入数据
        TableExportService.__write_timestamp(worksheet, ptr_r, 0)
        _, file_path = tempfile.mkstemp()
        workbook.save(file_path)
        return file_path

    # pylint: disable=R0914, R0915
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
            percent = 0 if summary['total_count'] == 0 else (
                summary['coverage_count'] * 100 / summary['total_count'])
            worksheet.write(ptr_r, 4, f'{percent:.2f}')
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
            percent = 0 if summary['total_count'] == 0 else (
                summary['coverage_count'] * 100 / summary['total_count'])
            worksheet.write(ptr_r, 4, f'{percent:.2f}')
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
            percent = 0 if summary['total_count'] == 0 else (
                summary['coverage_count'] * 100 / summary['total_count'])
            worksheet.write(ptr_r, 4, f'{percent:.2f}')
            ptr_r += 1

        if not ages_data:
            ptr_r += 1

        # 最后写合计
        worksheet.write(1, 2, total)
        worksheet.write(1, 3, coverage_total)
        percent = 0 if total == 0 else coverage_total * 100 / total
        worksheet.write(1, 4, f'{percent:.2f}')

        # 写入数据
        TableExportService.__write_timestamp(worksheet, ptr_r, 0)
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
            avg = (item['total_hours'] / item['total_users']) if item[
                'total_users'] > 0 else 0.0
            worksheet.write(ptr_r, 4, f'{avg:.02f}')
            avg = (item['total_hours']/item['total_coveraged_users']) if item[
                'total_coveraged_users'] > 0 else 0.0
            worksheet.write(ptr_r, 5, f'{avg:.02f}')
            ptr_r += 1

        # 写入数据
        TableExportService.__write_timestamp(worksheet, ptr_r, 0)
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
        TableExportService.__write_timestamp(worksheet, ptr_r, 0)
        _, file_path = tempfile.mkstemp()
        workbook.save(file_path)
        return file_path

    @staticmethod
    def export_records_for_user(data):
        '''Export records for user.
        Parameters
        ------
        data: list of dict{
            event_name: string,
            event_time: string,
            event_location: string,
            num_hours: string,
            create_time: string,
            role: string,
            status: string,
        }

        Returns
        ------
        string
            导出的excel文件路径
        '''
        if not data:
            raise BadRequest('导出内容不存在。')
        # 初始化excel
        workbook = xlwt.Workbook()
        worksheet = workbook.add_sheet('个人培训记录')
        style = xlwt.easyxf(('font: bold on; '
                             'align: wrap on, vert centre, horiz center'))
        name_col = worksheet.col(0)
        name_col.width = 256 * 35
        location_col = worksheet.col(2)
        location_col.width = 256 * 18
        status_col = worksheet.col(6)
        status_col.width = 256 * 18

        # 生成表头
        worksheet.write(0, 0, '培训项目', style)
        worksheet.write(0, 1, '时间', style)
        worksheet.write(0, 2, '地点', style)
        worksheet.write(0, 3, '学时', style)
        worksheet.write(0, 4, '参与身份', style)
        worksheet.write(0, 5, '创建时间', style)
        worksheet.write(0, 6, '审核状态', style)
        # 培训记录数据
        ptr_r = 1
        for item in data:
            worksheet.write(ptr_r, 0, item['event_name'], style)
            worksheet.write(ptr_r, 1,
                            item['event_time'].strftime('%Y-%m-%d'), style)
            worksheet.write(ptr_r, 2, item['event_location'], style)
            worksheet.write(ptr_r, 3, item['num_hours'], style)
            worksheet.write(ptr_r, 4, item['role'], style)
            worksheet.write(ptr_r, 5,
                            item['create_time'].strftime('%Y-%m-%d'), style)
            worksheet.write(ptr_r, 6, item['status'], style)
            ptr_r += 1
        # 写入数据
        TableExportService.__write_timestamp(worksheet, ptr_r, 0)
        _, file_path = tempfile.mkstemp()
        workbook.save(file_path)
        return file_path

    @staticmethod
    def export_attendance_sheet(data):
        '''Export attendance sheet for admin.
        Parameters
        ------
        data: list of Enrollment objects
        Returns
        ------
        string
            导出的excel文件路径
        '''
        if not data:
            raise BadRequest('导出内容不存在。')
        # 初始化excel
        workbook = xlwt.Workbook()
        worksheet = workbook.add_sheet('签到表')
        id_col = worksheet.col(0)
        id_col.width = 256 * 20
        department_col = worksheet.col(1)
        department_col.width = 256 * 20
        username_col = worksheet.col(2)
        username_col.width = 256 * 20
        style = xlwt.easyxf(('font: bold on; '
                             'align: wrap on, vert centre, horiz center'))
        style_value = xlwt.easyxf((
            'align: wrap on, vert centre, horiz center'))

        ptr_r = 0
        worksheet.write(ptr_r, 0, '培训活动编号', style_value)
        worksheet.write(ptr_r, 1, data[0].campus_event.id, style_value)
        ptr_r += 1
        sheet_name = data[0].campus_event.name + \
            '(' + data[0].campus_event.time.strftime('%Y-%m-%d') + ')' + '签到表'
        worksheet.write_merge(ptr_r, ptr_r, 0, 5, sheet_name, style)
        ptr_r += 1
        # 生成表头
        worksheet.write(ptr_r, 0, '序号', style)
        worksheet.write(ptr_r, 1, '院系', style)
        worksheet.write(ptr_r, 2, '工号', style)
        worksheet.write(ptr_r, 3, '姓名', style)
        worksheet.write(ptr_r, 4, '参与形式', style)
        worksheet.write(ptr_r, 5, '签到', style)
        # 已报名用户数据
        ptr_r += 1
        for idx, item in enumerate(data):
            worksheet.write(ptr_r, 0, idx+1, style_value)
            worksheet.write(ptr_r, 1,
                            item.user.department.name, style_value)
            worksheet.write(ptr_r, 2, item.user.username, style_value)
            worksheet.write(ptr_r, 3,
                            item.user.first_name+item.user.last_name,
                            style_value)
            ptr_r += 1
        # 写入数据
        TableExportService.__write_timestamp(worksheet, ptr_r, 0)
        _, file_path = tempfile.mkstemp()
        workbook.save(file_path)
        return file_path

    @staticmethod
    def __write_timestamp(sheet, row, col, lable='生成时间',
                          fmt='%Y-%m-%d %H:%M'):
        '''write current time into given sheet.'''
        time_str = now().strftime(fmt)
        sheet.write(row, col, f'{lable}:{time_str}')
