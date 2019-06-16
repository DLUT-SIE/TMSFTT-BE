'''Generate training records from xlsx file.'''
# pylint: disable=wrong-import-position,ungrouped-imports,invalid-name
# pylint: disable=missing-docstring
import logging
import sys
import os
import os.path as osp
import random
from datetime import datetime
from unittest.mock import patch, Mock

import django

sys.path.insert(0, os.path.abspath('.'))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'TMSFTT.settings_dev')
django.setup()

import xlrd
import pytz

from faker import Faker
from tqdm import tqdm
from django.db import transaction
from django.contrib.auth.models import Group
from django.utils.timezone import make_aware, now
from django.contrib.sites.models import Site

from infra.utils import prod_logger
from infra.models import Notification
from auth.models import User, Department
from auth.utils import (
    assign_perm, GenderConverter, TenureStatusConverter,
    EducationBackgroundConverter, TechnicalTitleConverter,
    TeachingTypeConverter, assign_model_perms_for_department,
    get_model_perms,
)
from auth.services import PermissionService
from training_program.models import Program
from training_event.models import CampusEvent, EventCoefficient, Enrollment
from training_record.models import (
    Record, RecordContent, RecordAttachment, CampusEventFeedback,
)
from training_review.models import ReviewNote
from secure_file.models import SecureFile


faker = Faker('zh_CN')
faker.seed(0)
prod_logger.setLevel(logging.WARNING)
manual_now = Mock()
manual_now.return_value = now()



cached_groups = {}
def get_or_create_group(department, group_type):
    group_name = (
        f'{department.name}-{department.raw_department_id}-{group_type}'
    )
    if group_name not in cached_groups:
        group, _ = Group.objects.get_or_create(name=group_name)
        cached_groups[group_name] = group
    return cached_groups[group_name]


administrative_departments = {}
def get_administrative_department(department):
    if department is None:
        return None
    if department.id not in administrative_departments:
        deps = [department]
        while department.super_department:
            department = department.super_department
            deps.append(department)
        if len(deps) < 3:
            admin_department = deps[0]
        else:
            admin_department = deps[-3]
        department = deps[0]
        administrative_departments[department.id] = admin_department
    return administrative_departments[department.id]


def get_dlut_department():
    department, _ = Department.objects.get_or_create(
        raw_department_id='10141', name='大连理工大学')
    return department


def get_dlut_admin():
    department = get_dlut_department()
    user, created = User.objects.get_or_create(
        username='tmsftt-admin',
        first_name='系统管理员',
        department=department,
        administrative_department=department
    )
    if created:
        user.groups.add(get_or_create_group(department, '管理员'),
                        get_personal_permissions_group())
    return user

def get_dlut_admin_group():
    return Group.objects.get_or_create(name='大连理工大学-10141-管理员')[0]


def get_personal_permissions_group():
    return Group.objects.get_or_create(name='个人权限')[0]


cached_programs = None
def make_programs():
    global cached_programs
    if cached_programs:
        return cached_programs
    candidate_programs = {
        Program.PROGRAM_CATEGORY_TRAINING: [
            '名师讲坛', '青年教学观摩', '教学基本功培训'],
        Program.PROGRAM_CATEGORY_PROMOTION: [
            '名师面对面', '学校青年教师讲课竞赛'],
        Program.PROGRAM_CATEGORY_TECHNOLOGY: [
            '课程技术服务', '智慧教室建设']
    }
    programs = []
    department = get_dlut_department()
    admin = get_dlut_admin()
    for category, names in candidate_programs.items():
        _programs = [Program.objects.create(
            name=name,
            department=department,
            category=category) for name in names]
        programs.extend(_programs)
        for program in _programs:
            PermissionService.assign_object_permissions(admin, program)
    cached_programs = programs
    return programs


def get_or_create_user(username, first_name, **kwargs):
    user, created = User.objects.get_or_create(
        username=username,
        first_name=first_name,
        **kwargs
    )
    if created:
        user.set_unusable_password()
    department = kwargs.get('department', None)
    while department is not None:
        group = get_or_create_group(department, '专任教师')
        user.groups.add(group)
        department = department.super_department
    return user, created


def row_parser_2018(row):
    return row[1:12]


def row_parser_2017(row):
    coef = 4 if row[5] == '专家' else 1
    return row[4], row[2], row[1], row[3], row[5], row[6], coef, 0


def read_workload_content(
        row_parser=row_parser_2018, start_row=1, year=2017,
        fpath='~/Desktop/TMSFTT/2018年教师发展工作量-全-0316-工号.xls'):
    '''Read xlsx file and generate records.'''
    workbook = xlrd.open_workbook(fpath)
    sheet = workbook.sheet_by_index(0)
    num_rows = sheet.nrows
    programs = {(p.name, p.category) for p in Program.objects.all()}
    events = {}
    coefficients = {}
    dlut_admin = get_dlut_admin()
    dlut_department = get_dlut_department()
    users = {x.username: x for x in User.objects.all()}
    for idx in tqdm(range(start_row, num_rows)):
        row = sheet.row_values(idx)
        try:
            (event_name, program_category, program_name, event_time,
             _, user_name, username,
             role, num_hours, coef, workload) = row_parser(row)
            role = EventCoefficient.ROLE_CHOICES_MAP[role.strip()]
            if not num_hours or not coef:
                coef = '1'
                num_hours = workload
            num_hours = int(num_hours)
            coef = int(coef)
            event_time = (
                datetime.strptime(f'{int(event_time)}', '%Y%m%d')
                .replace(hour=12, tzinfo=pytz.timezone('Asia/Shanghai'))
            )
        except ValueError:
            print(idx, row)
            raise

        if not username:
            related_users = User.objects.filter(first_name=user_name)
            if len(related_users) != 1:
                print(idx, row)
                continue
            username = related_users[0].username
        else:
            username = f'{int(username)}'
        user = users.get(username, None)
        if user is None:
            print(f'Unknown User at row {idx}: {user_name}({username})')
            continue

        # Program, Event and Coefficient
        program_key = (program_name, program_category)
        if program_key not in programs:
            programs[program_key] = Program.objects.create(
                name=program_name,
                department=dlut_department,
                category=Program.PROGRAM_CATEGORY_CHOICES_MAP[program_category]
            )
            PermissionService.assign_object_permissions(
                dlut_admin, programs[program_key])
        program = programs[program_key]
        event_key = (program_key, event_name, event_time)
        manual_now.return_value = event_time
        if event_key not in events:
            events[event_key] = CampusEvent.objects.create(
                name=event_name,
                time=event_time,
                location='大连理工大学',
                num_hours=num_hours,
                num_participants=0,
                program=program,
                deadline=event_time,
                num_enrolled=0,
                description='历史数据导入',
                reviewed=True,
            )
            PermissionService.assign_object_permissions(
                dlut_admin, events[event_key])
        event = events[event_key]
        try:
            Enrollment.objects.create(user=user, campus_event=event)
        except Exception as e:
            print(idx, row)
            raise
        event.num_participants += 1
        event.num_enrolled += 1
        event.save()

        coefficient_key = (event.id, role)
        if coefficient_key not in coefficients:
            coefficients[coefficient_key] = EventCoefficient.objects.create(
                campus_event=event,
                role=role,
                coefficient=coef
            )
        coefficient = coefficients[coefficient_key]

        # Record
        record = Record.objects.create(
            campus_event=event,
            user=user,
            status=Record.STATUS_FEEDBACK_SUBMITTED,
            event_coefficient=coefficient,
        )
        PermissionService.assign_object_permissions(user, record)

        #Feedback
        content = '历史培训记录导入。'
        CampusEventFeedback.objects.create(record=record, content=content)

def converter_get_or_default(converter, key, default=None):
    try:
        return converter.get_value(key)
    except Exception:
        return default if default else key


def read_departments_information(
        fpath='~/Desktop/TMSFTT/教师基本信息20190508(二级单位信息).xlsx'):
    workbook = xlrd.open_workbook(fpath)
    sheet = workbook.sheet_by_name('单位编码')
    num_rows = sheet.nrows
    dlut_department = get_dlut_department()
    id_to_departments = {
        dlut_department.raw_department_id: dlut_department,
    }
    rows = [sheet.row_values(i) for i in range(2, num_rows)]
    rows.sort(key=lambda x: 0 if x[8] == '10141' else int(x[8]))
    for row in tqdm(rows):
        dwid, dwmc, department_type, super_department_id = row[5:9]
        department, _ = Department.objects.get_or_create(
            raw_department_id=dwid,
            defaults={
                'name': dwmc,
                'department_type': department_type,
                'super_department': id_to_departments[super_department_id],
            },
        )
        id_to_departments[dwid] = department
        get_or_create_group(department, '管理员')
        get_or_create_group(department, '专任教师')


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
        fpath='~/Desktop/TMSFTT/教师相关信息20190424部分数据.xlsx'):
    departments = {x.raw_department_id: x for x in Department.objects.all()}
    workbook = xlrd.open_workbook(fpath)
    sheet = workbook.sheet_by_name('教师基本信息')
    num_rows = sheet.nrows
    users = {}
    personal_permissions_group = get_personal_permissions_group()

    def update_user_groups(user, handler):
        department = user.department
        administrative_department = user.administrative_department

        while department != administrative_department:
            handler(Group.objects.get(name=(
                f'{department.name}-{department.raw_department_id}-专任教师'))
            )
            department = department.super_department
        handler(Group.objects.get(
            name=f'{department.name}-{department.raw_department_id}-专任教师'))

    for idx in tqdm(range(2, num_rows)):
        row = sheet.row_values(idx)
        if row[0] in users:
            continue
        (zgh, jsxm, nl, xb, department_id, rxsj,
         rzzt, xl, zyjszc, rjlx) = extract_teacher_information(row)
        zgh = f'{int(zgh)}'
        department = departments.get(department_id, None)
        if department is None:
            print(f'Unknown department for user {jsxm}({zgh}) at row {idx}: {department_id}')
            continue
        administrative_department = get_administrative_department(department)
        kwargs = {
            'department': department,
            'administrative_department': administrative_department,
            'gender': User.GENDER_CHOICES_MAP.get(xb, User.GENDER_UNKNOWN),
            'age': nl,
            'onboard_time': rxsj,
            'tenure_status': rzzt,
            'education_background': xl,
            'technical_title': zyjszc,
            'teaching_type': rjlx,
        }
        user, created = get_or_create_user(zgh, jsxm, **kwargs)
        if created:
            update_user_groups(user, user.groups.add)
            user.groups.add(personal_permissions_group)
        users[zgh] = user
    return users


def assign_model_perms_for_special_groups():
    model_perms = get_model_perms()
    patch_for_model_perms = {
        Notification: {
            '个人权限': ['view'],
        },
        # Event
        CampusEvent: {
            '大连理工大学-管理员': ['add', 'view', 'change', 'delete', 'review'],
        },
        Enrollment: {
            '个人权限': ['add', 'delete'],
        },
        # Record
        Record: {
            '个人权限': ['add', 'view', 'change'],
        },
        RecordContent: {
            '个人权限': ['view'],
        },
        RecordAttachment: {
            '个人权限': ['view', 'delete'],
        },
        CampusEventFeedback: {
            '个人权限': ['add'],
        },
        # Review
        ReviewNote: {
            '个人权限': ['add', 'view'],
        },
        SecureFile: {
            '个人权限': ['view'],
        },
    }
    for model_class, perms_dict in patch_for_model_perms.items():
        model_perms[model_class].update(perms_dict)
    dlut_department = get_dlut_department()
    dlut_admin_group = get_dlut_admin_group()
    personal_permissions_group = get_personal_permissions_group()
    for model_class, perm_pairs in model_perms.items():
        for role, perms in perm_pairs.items():
            if role == '个人权限':
                group = personal_permissions_group
            elif role == '大连理工大学-管理员':
                group = dlut_admin_group
            else:
                group = get_or_create_group(dlut_department, role)
            for perm in perms:
                perm_name = (
                    f'{model_class._meta.app_label}.'
                    f'{perm}_{model_class._meta.model_name}'
                )
                assign_perm(perm_name, group)


def assign_model_perms():
    departments = {
        x.raw_department_id: x
        for x in Department.objects.all().exclude(name='大连理工大学')
    }
    for department in tqdm(departments.values()):
        assign_model_perms_for_department(department)


def populate_initial_data():
    site_data = {
        'domain': 'ctfdpeixun.dlut.edu.cn',
        'name': '大连理工大学专任教师教学培训管理系统'
    }
    site, created = Site.objects.get_or_create(
        id=1,
        defaults=site_data,
    )
    if not created:
        for attr, value in site_data.items():
            setattr(site, attr, value)
        site.save()
    get_dlut_admin()
    user, _ = User.objects.get_or_create(
        username='notification-robot',
        defaults={'first_name': '系统通知'}
    )
    user.set_unusable_password()
    assign_model_perms_for_special_groups()


@transaction.atomic
def populate(base='~/Desktop/TMSFTT'):
    print('Populating initial data')
    populate_initial_data()
    print('Creating departments')
    read_departments_information(
        fpath=osp.join(base, '教师基本信息20190508(二级单位信息).xlsx')
    )
    print('Assigning model permissions')
    assign_model_perms()
    print('Creating users')
    read_teachers_information(
        fpath=osp.join(base, '教师相关信息20190424部分数据.xlsx')
    )
    print('Creating workload for 2017')
    read_workload_content(
        row_parser=row_parser_2017,
        start_row=2,
        year=2017,
        fpath=osp.join(base, '2017年教师发展工作量-全-0316-工号.xlsx'),
    )
    print('Creating workload for 2018')
    read_workload_content(
        row_parser=row_parser_2018,
        start_row=1,
        year=2018,
        fpath=osp.join(base, '2018年教师发展工作量-全-0316-工号-获奖情况.xls'),
    )


@patch('django.utils.timezone.now', manual_now)
def main():
    if len(sys.argv) < 2:
        populate()
        return
    cmd = sys.argv[1]
    if cmd == 'initial':
        populate_initial_data()
    elif cmd == 'model_perms':
        assign_model_perms()
        assign_model_perms_for_special_groups()
    elif cmd == '2018':
        path = sys.argv[2]
        read_workload_content(
           row_parser=row_parser_2018,
           start_row=1,
           year=2018,
           fpath=path,
        )


if __name__ == '__main__':
    with transaction.atomic():
        main()