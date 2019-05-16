'''Celery tasks.'''
from celery import shared_task

from django.db import transaction
from django.utils.dateparse import parse_datetime
from django.utils.timezone import make_aware
from auth.models import (
    User, Department, DepartmentInformation, TeacherInformation)

from infra.utils import prod_logger

DLUT_ID = '10141'
DLUT_NAME = '大连理工大学'


def _update_from_department_information():
    '''Scan table DepartmentInformation and update related tables.'''
    prod_logger.info('开始扫描并更新部门信息')

    dlut, _ = Department.objects.get_or_create(raw_department_id=DLUT_ID)
    if dlut.name is None or dlut.name != DLUT_NAME:
        dlut.name = DLUT_NAME
        dlut.save()

    raw_departments = DepartmentInformation.objects.all()
    dwid_to_department = {}
    department_id_to_administrative = {}
    for raw_department in raw_departments:
        department, _ = Department.objects.get_or_create(
            raw_department_id=raw_department.dwid,
            defaults={'name': raw_department.dwmc})

        updated = False
        # 同步隶属单位
        if (department.super_department is None or
                department.super_department.raw_department_id !=
                raw_department.lsdw):
            super_department_name = DepartmentInformation.objects.get(
                dwid=raw_department.lsdw).dwmc
            super_department, _ = Department.objects.get_or_create(
                raw_department_id=raw_department.lsdw,
                defaults={'name': super_department_name}
            )

            department.super_department = super_department
            updated = True

        # 同步单位类型
        if department.department_type != raw_department.dwlx:
            department.department_type = raw_department.dwlx
            updated = True

        # 同步单位名称
        if department.name != raw_department.dwmc:
            department.name = raw_department.dwmc
            updated = True
        if updated:
            department.save()

        dwid_to_department[raw_department.dwid] = department

        if department.super_department == dlut:
            # 二级部门的administrative为本身
            department_id_to_administrative[department.id] = department
        else:
            # 非二级部门的administrative暂为superdepartment
            department_id_to_administrative[department.id] = (
                department.super_department
            )

    for department_id in department_id_to_administrative:
        same_administrative = []
        administrative = department_id_to_administrative[department_id]
        while administrative.id != department_id:
            same_administrative.append(department_id)
            department_id = administrative.id
            administrative = department_id_to_administrative[department_id]
        for item_id in same_administrative:
            department_id_to_administrative[item_id] = administrative
    # TODO(youchen): Create related groups

    prod_logger.info('部门信息更新完毕')

    return dwid_to_department, department_id_to_administrative


def _update_from_teacher_information(dwid_to_department,
                                     department_id_to_administrative):
    '''Scan table TeacherInformation and update related tables.'''
    prod_logger.info('开始扫描并更新用户信息')
    raw_users = TeacherInformation.objects.all()
    raw_department_ids = [
        f'{dep.raw_department_id}'
        for dep in department_id_to_administrative.values()]
    for raw_user in raw_users:
        user, created = User.objects.get_or_create(username=raw_user.zgh)
        if created:
            user.set_unusable_password()
        user.first_name = raw_user.jsxm

        if raw_user.xy not in raw_department_ids:
            warn_msg = (
                f'职工号为{user.username}的教师'
                f'使用了一个系统中不存在的学院{raw_user.xy}'
            )
            prod_logger.warning(warn_msg)
        else:
            user.department = dwid_to_department.get(raw_user.xy)
            user.administrative_department = (
                department_id_to_administrative[user.department.id]
            )

        user.gender = User.GENDER_CHOICES_MAP[raw_user.get_xb_display()]
        raw_age = int(raw_user.nl) if raw_user.nl else 0
        user.age = raw_age
        if raw_user.rxsj and user.onboard_time != raw_user.rxsj:
            user.onboard_time = make_aware(
                parse_datetime(f'{raw_user.rxsj}T12:00:00'))

        user.tenure_status = raw_user.get_rzzt_display()
        user.education_background = raw_user.get_xl_display()
        user.technical_title = raw_user.get_zyjszc_display()
        user.teaching_type = raw_user.get_rjlx_display()
        user.cell_phone_number = raw_user.sjh
        user.email = raw_user.yxdz

        user.save()
    prod_logger.info('用户信息更新完毕')


@shared_task
@transaction.atomic()
def update_teachers_and_departments_information():
    '''Scan table TBL_DW_INFO and TBL_JB_INFO, update related tables.'''
    try:
        dwid_to_department, department_id_to_administrative = (
            _update_from_department_information()
        )

        _update_from_teacher_information(dwid_to_department,
                                         department_id_to_administrative)
    except Exception:
        prod_logger.exception('教师信息或部门信息更新失败')
