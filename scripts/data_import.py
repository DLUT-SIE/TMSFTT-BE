'''Generate training records from xlsx file.'''
# pylint: disable=wrong-import-position,ungrouped-imports,invalid-name
# pylint: disable=missing-docstring
import sys
import os
import random
from datetime import datetime, timedelta

import django

sys.path.insert(0, os.path.abspath('.'))
os.environ['DJANGO_SETTINGS_MODULE'] = 'TMSFTT.settings_dev'
django.setup()

import xlrd

from faker import Faker
from django.db import transaction
from django.contrib.auth.models import Group
from django.utils.timezone import make_aware, now

from auth.models import User, Department
from auth.utils import assign_perm
from auth.services import (
    GenderConverter, TenureStatusConverter, EducationBackgroundConverter,
    TechnicalTitleConverter, TeachingTypeConverter
)
from infra.models import Notification
from training_program.models import Program
from training_event.models import CampusEvent, EventCoefficient, Enrollment
from training_record.models import (
    Record, RecordContent, RecordAttachment, CampusEventFeedback
)
from training_review.models import ReviewNote


faker = Faker('zh_CN')
faker.seed(0)


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


__cached_groups = {}
def get_or_create_group(department, group_type):
    group_name = f'{department.name}-{group_type}'
    if group_name not in __cached_groups:
        group, _ = Group.objects.get_or_create(name=group_name)
        __cached_groups[group_name] = group
    return __cached_groups[group_name]


def get_dlut_department_and_group():
    department, _ = Department.objects.get_or_create(
        raw_department_id='10141', name='大连理工大学')
    return department, get_or_create_group(department, '专任教师')


def make_programs():
    programs = {
        Program.PROGRAM_CATEGORY_TRAINING: [
            '名师讲坛', '青年教学观摩', '教学基本功培训'],
        Program.PROGRAM_CATEGORY_PROMOTION: [
            '名师面对面', '学校青年教师讲课竞赛'],
        Program.PROGRAM_CATEGORY_TECHNOLOGY: [
            '课程技术服务', '智慧教室建设']
    }
    res = []
    department, group = get_dlut_department_and_group()
    for category, names in programs.items():
        res.extend(Program(
            name=name,
            department=department,
            category=category) for name in names)
    names = [p.name for p in res]
    res = Program.objects.bulk_create(res)
    res = Program.objects.filter(name__in=names)
    for program in res:
        assign_perm('view_program', group, program)
    return res


def read_worload_content(
        users, departments,
        fpath='~/Desktop/TMSFTT/2018年教师发展工作量-全-0315.xls'):
    '''Read xlsx file and generate records.'''
    users_dict = {u.first_name: u for u in users}
    departments_dict = {d.name: d for d in departments}
    workbook = xlrd.open_workbook(fpath)
    sheet = workbook.sheet_by_name('原始')
    num_rows = sheet.nrows
    programs = make_programs()
    event_to_program = {}
    events = {}
    coefficients = {}
    role_map = {
        '主讲': '主讲人',
        '观摩': '参与教师',
    }
    _, dlut_group = get_dlut_department_and_group()
    for idx, row in enumerate((sheet.row_values(i)
                               for i in range(1, num_rows))):
        sys.stdout.flush()
        sys.stdout.write(f'{idx:4d} / {num_rows:4d} \r')
        try:
            (event_name, department_name, user_name,
             role, num_hours, coef, workload) = row[1:8]
            if not role:
                role = '观摩'
            elif '新增' in role:
                role = '观摩'
            elif '专家' in role:
                role = '主讲'
            role = EventCoefficient.ROLE_CHOICES_MAP[role_map[role]]
            if not num_hours or not coef:
                coef = '1'
                num_hours = workload
            num_hours = int(num_hours)
            coef = int(coef)
        except ValueError:
            print(idx, row)
            raise
        if not department_name:
            continue

        # User and Department
        department_name = clean_department_name(department_name)
        department = departments_dict.get(
            department_name, random.choice(departments))
        teachers_group = get_or_create_group(department, '专任教师')
        user = users_dict.get(
            user_name, random.choice(users))
        user.groups.add(teachers_group, dlut_group)

        # Program, Event and Coefficient
        program = event_to_program.setdefault(
            event_name, random.choice(programs))
        if event_name not in events:
            events[event_name] = CampusEvent.objects.create(
                name=event_name,
                program=program,
                time=now(),
                deadline=now()+timedelta(days=random.randint(1, 100)),
                location='大连理工大学',
                num_hours=num_hours,
                num_participants=random.randint(20, 100),
                description=faker.text(100)
            )
        event = events[event_name]
        assign_perm('view_campusevent', dlut_group, event)
        if (event.id, role) not in coefficients:
            coefficients[(event.id, role)] = EventCoefficient.objects.create(
                campus_event=event,
                role=role,
                coefficient=coef
            )
        event_coef = coefficients[(event.id, role)]

        # Record
        record = Record.objects.create(
            campus_event=event,
            user=user,
            status=Record.STATUS_FEEDBACK_REQUIRED,
            event_coefficient=event_coef,
        )
        assign_perm('view_record', user, record)
    print()


def converter_get_or_default(converter, key, default=None):
    try:
        return converter.get_value(key)
    except Exception:
        return default if default else key


def read_departments_information(
        fpath='~/Desktop/TMSFTT/教师相关信息20190424部分数据.xlsx'):
    workbook = xlrd.open_workbook(fpath)
    sheet = workbook.sheet_by_name('单位编码')
    num_rows = sheet.nrows
    dlut_department, dlut_teachers_group = get_dlut_department_and_group()
    departments = []
    for row in (sheet.row_values(i) for i in range(1, num_rows)):
        dwid, dwmc, parent = row[:3]
        if parent != '000001':
            continue
        if not any(x in dwmc for x in ['学部', '学院']):
            continue
        if any(x in dwmc for x in ['体育', '大连', '国防', '国际', '远程']):
            continue
        departments.append(Department(
            raw_department_id=dwid,
            name=dwmc,
        ))
    res = Department.objects.bulk_create(departments)
    res = Department.objects.filter(
        raw_department_id__in=[d.raw_department_id for d in departments])
    for department in res:
        assign_perm('view_department', dlut_teachers_group, department)
    return res


def extract_teacher_information(row):
    zgh, jsxm, csrq, xb, xy, rxsj, rzzt, xl, zyjszc, rjlx = row[:10]
    if csrq:
        csrq = make_aware(datetime.strptime(csrq, '%Y-%m-%d'))
        nl = (now() - csrq).days // 365
    else:
        nl = 0
    if rxsj:
        rxsj = make_aware(datetime.strptime(rxsj, '%Y-%m-%d'))
    else:
        rxsj = None
    # Convert to human-readable strings
    xb = converter_get_or_default(GenderConverter, xb)
    rzzt = converter_get_or_default(TenureStatusConverter, rzzt)
    xl = converter_get_or_default(EducationBackgroundConverter, xl)
    zyjszc = converter_get_or_default(TechnicalTitleConverter, zyjszc)
    rjlx = converter_get_or_default(TeachingTypeConverter, rjlx)
    return zgh, jsxm, nl, xb, xy, rxsj, rzzt, xl, zyjszc, rjlx


def read_teachers_information(
        departments,
        fpath='~/Desktop/TMSFTT/教师相关信息20190424部分数据.xlsx'):
    workbook = xlrd.open_workbook(fpath)
    sheet = workbook.sheet_by_name('教师基本信息')
    num_rows = sheet.nrows
    users = []
    existing_users = set()
    for row in (sheet.row_values(i) for i in range(2, num_rows)):
        if row[0] in existing_users:
            continue
        existing_users.add(row[0])
        (zgh, jsxm, nl, xb, _, rxsj,
         rzzt, xl, zyjszc, rjlx) = extract_teacher_information(row)
        users.append(User(
            username=zgh,
            first_name=jsxm,
            department=random.choice(departments),
            gender=User.GENDER_CHOICES_MAP.get(xb, User.GENDER_UNKNOWN),
            age=nl,
            onboard_time=rxsj,
            tenure_status=rzzt,
            education_background=xl,
            technical_title=zyjszc,
            teaching_type=rjlx
        ))
    res = User.objects.bulk_create(users)
    res = User.objects.filter(username__in=[u.username for u in users])
    return res


def assign_model_perms(departments):
    models = {
        # Auth
        Department: {
            '管理员': ['add', 'view', 'change'],
            '专任教师': ['view'],
        },
        # Infra
        Notification: {
            '管理员': ['view'],
            '专任教师': ['view'],
        },
        # Program
        Program: {
            '管理员': ['add', 'view', 'change'],
            '专任教师': ['view'],
        },
        # Event
        CampusEvent: {
            '管理员': ['add', 'view', 'change'],
            '专任教师': ['view'],
        },
        Enrollment: {
            '管理员': ['view'],
            '专任教师': ['add'],
        },
        # Record
        Record: {
            '管理员': ['add', 'view', 'change'],
            '专任教师': ['add', 'view', 'change'],
        },
        RecordContent: {
            '管理员': ['view'],
            '专任教师': ['add', 'view', 'change'],

        },
        RecordAttachment: {
            '管理员': ['view'],
            '专任教师': ['add', 'view', 'change'],
        },
        CampusEventFeedback: {
            '管理员': ['view'],
            '专任教师': ['add', 'view', 'change'],
        },
        # Review
        ReviewNote: {
            '管理员': ['add', 'view', 'change'],
            '专任教师': ['add', 'view', 'change'],
        },
    }
    for department in departments:
        for model_class, perm_pairs in models.items():
            for role, perms in perm_pairs.items():
                group = get_or_create_group(department, role)
                for perm in perms:
                    perm_name = (
                        f'{model_class._meta.app_label}.'
                        f'{perm}_{model_class._meta.model_name}'
                    )
                    assign_perm(perm_name, group)


@transaction.atomic
def populate():
    departments = read_departments_information()
    users = read_teachers_information(departments)
    read_worload_content(users, departments)
    assign_model_perms(departments)


if __name__ == '__main__':
    populate()
