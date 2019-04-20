'''Generate training records from xlsx file.'''
import sys
import os
import random
import django

sys.path.insert(0, os.path.abspath('.'))
os.environ['DJANGO_SETTINGS_MODULE'] = 'TMSFTT.settings_dev'
django.setup()

import xlrd

from faker import Faker
from model_mommy import mommy
from django.db import transaction
from django.contrib.auth.models import Group

from auth.models import User, Department
from auth.utils import assign_perm
from training_program.models import Program
from training_event.models import CampusEvent
from training_record.models import Record


def clean_department_name(department_name):
    '''Unify department name.'''
    department_name = department_name.strip()
    mappings = {
        '人文': '人文与社会科学学部',
        '人文学院': '人文与社会科学学部',
        '人文学部': '人文与社会科学学部',
        '人文与社会科学学部-中文系': '人文与社会科学学部',
        '人文与社会科学学部-法律系': '人文与社会科学学部',
        '人文与社会科学学部-新闻传播学系': '人文与社会科学学部',

        '物理学院': '物理与光电工程学院',
        '光仪学院': '物理与光电工程学院',
        '光电工程与仪器科学学院': '物理与光电工程学院',

        '外语': '外国语学院',

        '材料': '材料科学与工程学院',
        '材料学院': '材料科学与工程学院',

        '研院': '研究生院',

        '数学': '数学科学学院',

        '机械': '机械工程学院',
        '机械学院': '机械工程学院',
        '机械工程与材料能源学部-机械工程学院': '机械工程学院',

        '电信': '电子信息与电气工程学部',
        '电信学部': '电子信息与电气工程学部',
        '电气': '电子信息与电气工程学部',
        '电气工程学院': '电子信息与电气工程学部',
        '计算机科学与技术学院': '电子信息与电气工程学部',
        '生物医学工程系': '电子信息与电气工程学部',
        '信息与通信工程': '电子信息与电气工程学部',
        '信息与通信工程学院': '电子信息与电气工程学部',
        '控制科学与工程学院': '电子信息与电气工程学部',

        '建艺': '建筑与艺术学院',
        '建艺学院': '建筑与艺术学院',

        '能动学院': '能源与动力学院',

        '管理': '管理与经济学部',
        '管经学部': '管理与经济学部',
        '工商管理学院': '管理与经济学部',
        '管理与经济学部-经济研究所': '管理与经济学部',
        '管理科学与工程学院': '管理与经济学部',

        '化工与环境生命学部-化学学院': '化工与环境生命学部',
        '化工与环境生命学部-化工学院': '化工与环境生命学部',
        '化工与环境生命学部-制药科学与技术学院': '化工与环境生命学部',
        '制药科学与技术学院': '化工与环境生命学部',
        '化工与环境生命学部-生命科学与技术学院': '化工与环境生命学部',
        '生命': '化工与环境生命学部',
        '生命科学与技术学院': '化工与环境生命学部',
        '化学': '化工与环境生命学部',
        '化工': '化工与环境生命学部',
        '生命学院': '化工与环境生命学部',
        '环境学院': '化工与环境生命学部',
        '化工学部': '化工与环境生命学部',
        '化学学院': '化工与环境生命学部',
        '化工学院': '化工与环境生命学部',
        '化工机械学院': '化工与环境生命学部',

        '运载': '运载工程与力学学部',
        '力学': '运载工程与力学学部',
        '运载学部': '运载工程与力学学部',
        '交通运输学院': '运载工程与力学学部',
        '工程力学系': '运载工程与力学学部',
        '船舶工程学院': '运载工程与力学学部',
        '航空航天学院': '运载工程与力学学部',

        '马院': '马克思主义学院',
        '人文与社会科学学部-马克思主义学院': '马克思主义学院',

        '建设工程学部-土木工程学院': '建设工程学部',
        '建工': '建设工程学部',
        '建工学部': '建设工程学部',
        '水利工程学院': '建设工程学部',
        '深海工程研究中心': '建设工程学部',

        '微电子': '微电子学院',

        '盘锦': '盘锦校区',
        '盘锦校区基础教学部': '盘锦校区',
        '盘锦校区生命与医药学院': '盘锦校区',

        '体教部': '体育教学部',

        '开发区校区': '软件学院',
        '国家示范性软件学院': '软件学院',
        '大连理工大学-立命馆大学国际信息与软件学院': '软件学院',
    }
    return mappings.get(department_name, department_name)


@transaction.atomic
def read_content(fpath='~/Desktop/TMSFTT/2018年教师发展工作量-全-0315.xls'):
    '''Read xlsx file and generate records.'''
    faker = Faker('zh_CN')
    faker.seed(0)
    workbook = xlrd.open_workbook(fpath)
    sheet = workbook.sheet_by_name('原始')
    num_rows = sheet.nrows
    programs = {}
    events = {}
    departments = {}
    groups = {}
    users = {}
    for idx, row in enumerate((sheet.row_values(i)
                               for i in range(1, num_rows))):
        sys.stdout.flush()
        sys.stdout.write(f'{idx:4d} / {num_rows:4d} \r')
        try:
            event_name, department_name, user_name = row[1:4]
        except ValueError:
            print(row)
            raise
        if not department_name:
            continue
        department_name = clean_department_name(department_name)
        if department_name not in departments:
            departments[department_name] = mommy.make(
                Department, name=department_name)
        department = departments[department_name]
        regular_group_name = f'{department_name}(普通教师)'
        if regular_group_name not in groups:
            groups[regular_group_name] = mommy.make(
                Group, name=f'{department_name}(普通教师)')
        regular_group = groups[regular_group_name]
        admin_group_name = f'{department_name}(院系管理员)'
        if admin_group_name not in groups:
            groups[admin_group_name] = mommy.make(
                Group, name=f'{department_name}(院系管理员)')
        admin_group = groups[admin_group_name]
        if user_name not in users:
            users[user_name] = mommy.make(
                User, username=f'username{idx}', first_name=user_name)
        user = users[user_name]
        user.groups.add(regular_group)
        if event_name not in programs:
            programs[event_name] = mommy.make(
                Program,
                name=faker.company_prefix(),
                department=department,
                category__name='教学培训',
                )
        program = programs[event_name]
        if event_name not in events:
            events[event_name] = mommy.make(
                CampusEvent,
                name=event_name,
                program=program,
                location=faker.street_address(),
                num_hours=random.randint(1, 5),
                num_participants=random.randint(20, 200),
                description=faker.text(100),
                )
        event = events[event_name]
        record = mommy.make(
            Record,
            campus_event=event,
            user=user)

        assign_perm('view_record', user, record)
        assign_perm('change_record', user, record)
        assign_perm('delete_record', user, record)

        assign_perm('view_record', admin_group, record)
        assign_perm('change_record', admin_group, record)
        assign_perm('delete_record', admin_group, record)
    for name, group in groups.items():
        if name.endswith('(院系管理员)'):
            assign_perm('training_program.add_programform', group)
            assign_perm('training_program.add_programcategory', group)
            assign_perm('training_program.add_program', group)

            assign_perm('training_event.add_campusevent', group)

            assign_perm('training_record.add_record', group)
            assign_perm('training_record.add_recordcontent', group)
            assign_perm('training_record.add_recordattachment', group)

        assign_perm('training_program.view_programform', group)
        assign_perm('training_program.view_programcategory', group)
        assign_perm('training_program.view_program', group)
        assign_perm('training_event.view_campusevent', group)
        assign_perm('training_record.view_record', group)
        assign_perm('training_record.view_recordcontent', group)
        assign_perm('training_record.view_recordattachment', group)
    print()


if __name__ == '__main__':
    read_content()
