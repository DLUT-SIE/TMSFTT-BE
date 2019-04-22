'''Celery tasks.'''
from celery import shared_task


@shared_task
def update_users_from_teacher_information():
    '''Scan table TBL_JB_INFO and update related tables.'''
    # TODO(youchen): Do update


@shared_task
def update_departments_from_teacher_information():
    '''Scan table TBL_DW_INFO and update related tables.'''
    # TODO(youchen): Do update
