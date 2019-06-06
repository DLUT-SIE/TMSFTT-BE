'''Celery tasks.'''
from datetime import datetime

from celery import shared_task
from tqdm import tqdm

from django.db import transaction
from django.utils.dateparse import parse_datetime
from django.utils.timezone import make_aware, now
from django.contrib.auth.models import Group
from auth.models import (
    User, Department, DepartmentInformation, TeacherInformation, UserGroup)
from auth.utils import assign_model_perms_for_department

from infra.utils import prod_logger

DLUT_ID = '10141'
DLUT_NAME = '大连理工大学'


def update_user_groups(handler, trace_department, dlut):
    '''增删某一群用户的department链上的group'''
    while trace_department.raw_department_id != dlut.raw_department_id:
        handler(Group.objects.get(
            name=f'{trace_department.name}-专任教师'))
        trace_department = trace_department.super_department
    handler(Group.objects.get(
        name=f'{trace_department.name}-专任教师'))


def _update_from_department_information():
    # pylint: disable=R0912
    # pylint: disable=R0915
    # pylint: disable=R1702
    # pylint: disable=R0914
    '''Scan table DepartmentInformation and update related tables.'''
    prod_logger.info('开始扫描并更新部门信息')
    # 校区初始化
    dlut, _ = Department.objects.get_or_create(raw_department_id=DLUT_ID,
                                               defaults={'name': DLUT_NAME})
    raw_departments = DepartmentInformation.objects.exclude(dwid=DLUT_ID)
    dwid_to_department = {}
    department_id_to_administrative = {}

    def update_administrative(department_id_to_administrative):
        # 更新administrative
        for department_id in department_id_to_administrative:
            same_administrative = []
            administrative = department_id_to_administrative[department_id]
            while administrative.id != department_id:
                same_administrative.append(department_id)
                department_id = administrative.id
                administrative = department_id_to_administrative[department_id]
            for item_id in same_administrative:
                department_id_to_administrative[item_id] = administrative
        return department_id_to_administrative

    def update_group_and_perms(department, created):
        # 同步group
        group_names = [f'{department.name}-管理员',
                       f'{department.name}-专任教师']
        for group_name in group_names:
            Group.objects.get_or_create(name=group_name)
        if created:
            assign_model_perms_for_department(department)

    def find_all_child_department(super_department):
        # 将当前department的所有叶子结点返回
        childs = []
        child_departments = Department.child_departments.all()
        if child_departments:
            for child_department in child_departments:
                childs.extend(find_all_child_department(child_department))
        else:
            childs.extend([super_department])
        return childs
    try:
        for raw_department in tqdm(raw_departments):
            department, created = Department.objects.get_or_create(
                raw_department_id=raw_department.dwid,
                defaults={'name': raw_department.dwmc})
            update_group_and_perms(department, created)
            updated = False
            # 同步隶属单位
            if (department.super_department is None or
                    department.super_department.raw_department_id !=
                    raw_department.lsdw):
                # DepartmentInformation中不含大连理工大学
                super_department_name = DLUT_NAME
                if raw_department.lsdw != DLUT_ID:
                    super_department_name = DepartmentInformation.objects.get(
                        dwid=raw_department.lsdw).dwmc
                super_department, created = Department.objects.get_or_create(
                    raw_department_id=raw_department.lsdw,
                    defaults={'name': super_department_name}
                )
                update_group_and_perms(super_department, created)
                # 将老师从原有group中删除
                if department.super_department:
                    child_departments = find_all_child_department(
                        department.super_department)
                    for department in child_departments:
                        teachers = User.objects.filter(department=department)
                        UserGroup.objects.filter(
                            user__in=teachers,
                            group__name__endswith='-专任教师').delete()
                        teachers.update(department=None)
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
            if dlut in (department.super_department,
                        department.super_department.super_department):
                # 校区和二级部门的administrative为本身
                department_id_to_administrative[department.id] = department
            else:
                # 非二级部门的administrative暂为superdepartment
                department_id_to_administrative[department.id] = (
                    department.super_department
                )
    except Exception as exc:
        prod_logger.exception('部门信息更新失败,单位号:%s, excepiton:%s',
                              raw_department.dwid, exc)
        raise
    department_id_to_administrative = update_administrative(
        department_id_to_administrative)
    for raw_department in raw_departments:
        department, created = Department.objects.get_or_create(
            raw_department_id=raw_department.dwid,
            defaults={'name': raw_department.dwmc})
        dwid_to_department[raw_department.dwid] = department

    prod_logger.info('部门信息更新完毕')

    return dwid_to_department, department_id_to_administrative


def _update_from_teacher_information(dwid_to_department,
                                     department_id_to_administrative):
    '''Scan table TeacherInformation and update related tables.'''
    prod_logger.info('开始扫描并更新用户信息')
    dlut, _ = Department.objects.get_or_create(raw_department_id=DLUT_ID,
                                               defaults={'name': DLUT_NAME})
    raw_users = TeacherInformation.objects.all()
    try:
        for raw_user in tqdm(raw_users):
            user, created = User.all_objects.get_or_create(
                username=raw_user.zgh)
            if created:
                user.set_unusable_password()
            user.first_name = raw_user.jsxm
            if raw_user.xy not in dwid_to_department:
                warn_msg = (
                    f'职工号为{user.username}的教师'
                    f'使用了一个系统中不存在的学院{raw_user.xy}'
                )
                UserGroup.objects.filter(
                    user=user,
                    group__name__endswith='-专任教师').delete()
                user.department = None
                prod_logger.warning(warn_msg)
            elif user.department != dwid_to_department.get(raw_user.xy):
                if user.department:
                    update_user_groups(user.groups.remove, user.department,
                                       dlut)
                user.department = dwid_to_department.get(raw_user.xy)
                user.administrative_department = (
                    department_id_to_administrative[user.department.id]
                )
                update_user_groups(user.groups.add, user.department, dlut)
            user.gender = User.GENDER_CHOICES_MAP.get(
                raw_user.get_xb_display(), User.GENDER_UNKNOWN)
            user.age = 0
            if raw_user.csrq:
                birthday = make_aware(
                    datetime.strptime(raw_user.csrq, '%Y-%m-%d'))
                user.age = (now() - birthday).days // 365
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
    except Exception as exc:
        prod_logger.exception('用户信息更新失败,职工号:%s, exception:%s',
                              raw_user.zgh, exc)
        raise
    prod_logger.info('用户信息更新完毕')


@shared_task
@transaction.atomic()
def update_teachers_and_departments_information():
    '''Scan table TBL_DW_INFO and TBL_JB_INFO, update related tables.'''
    dwid_to_department, department_id_to_administrative = (
        _update_from_department_information()
    )

    _update_from_teacher_information(dwid_to_department,
                                     department_id_to_administrative)
