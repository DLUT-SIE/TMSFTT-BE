'''Generate training records from xlsx file 190910.'''
# pylint: disable=wrong-import-position,ungrouped-imports,invalid-name
# pylint: disable=missing-docstring
import sys
import os

import django

sys.path.insert(0, os.path.abspath('.'))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'TMSFTT.settings_dev')
django.setup()

from tqdm import tqdm
import xlrd
from django.db import transaction

from auth.models import User
from auth.services import PermissionService
from training_program.models import Program
from training_event.models import CampusEvent, EventCoefficient
from training_record.models import Record, CampusEventFeedback

def row_parser(row):
    return [row[0], row[1], row[2], row[3], row[4]]

def read_workload_content(
        row_parser=row_parser, start_row=2,
        fpath='~/Desktop/TMSFTT/教学工作坊-教学创新大赛.xlsx'):
    '''Read xlsx file and generate records.'''
    workbook = xlrd.open_workbook(fpath)
    sheet = workbook.sheet_by_index(0)
    num_rows = sheet.nrows

    event_name = sheet.cell_value(0, 0)
    event = CampusEvent.objects.get(name=event_name)
    if event is None:
        raise Exception('Event ({}) is not exist!'.format(event_name))


    for idx in tqdm(range(start_row, num_rows)):
        row = sheet.row_values(idx)
        try:
            (department_name, first_name, username, attend, role) = row_parser(row)
        except ValueError:
            print(idx, row)
            raise

        if attend != '是':
            continue

        if username:
            username = str(int(username))
            try:
                user = User.objects.get(username=username)
            except Exception:
                print('学号为{}的老师不存在!'.format(username))
                raise
        elif department_name:
            users = User.objects.filter(first_name=first_name)
            user = None
            if len(users) == 1:
                user = users[0]
            elif len(users) > 1:
                for _user in users:
                    if _user.department:
                        if(department_name in
                            (_user.department.name,
                            _user.department.super_department.name)):
                            user = _user
        else:
            users = User.objects.filter(first_name=first_name)
            user = None
            if len(users) > 0:
                user = users[0]

        if user is None:
            print(f'Unknown User at row {idx}: {username}({username})')
            continue

        role = (EventCoefficient.ROLE_EXPERT
                if role == '专家' else EventCoefficient.ROLE_PARTICIPATOR)
        # Record
        coefficient = EventCoefficient.objects.get(
            campus_event=event,
            role=role
        )

        record = Record.objects.create(
            campus_event=event,
            user=user,
            status=Record.STATUS_FEEDBACK_SUBMITTED,
            event_coefficient=coefficient,
        )
        PermissionService.assign_object_permissions(user, record)

        CampusEventFeedback.objects.create(record=record, content='import by admin')

def main():
    path = sys.argv[1]
    read_workload_content(
        row_parser=row_parser,
        start_row=2,
        fpath=path,
    )

if __name__ == '__main__':
    with transaction.atomic():
        main()
