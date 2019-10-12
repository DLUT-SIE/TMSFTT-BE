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
from training_record.models import Record

def row_parser0(row):
    return [row[1], row[2], row[10]]

def read_workload_content(
        row_parser=row_parser0, start_row=2,
        fpath='~/Desktop/TMSFTT/骨干教师教学能力提升培训班-考勤表-更新至第七场培训.xlsx'):
    '''Read xlsx file and generate records.'''
    workbook = xlrd.open_workbook(fpath)
    sheet = workbook.sheet_by_index(0)
    num_rows = sheet.nrows
    program = Program.objects.get(name='骨干教师教学能力提升培训班')
    events = CampusEvent.objects.filter(program=program)
    event = events[6]
    for idx in tqdm(range(start_row, num_rows)):
        row = sheet.row_values(idx)
        try:
            (department_name, username, attend) = row_parser(row)
            role = EventCoefficient.ROLE_PARTICIPATOR
        except ValueError:
            print(idx, row)
            raise

        users = User.objects.filter(first_name=username)
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
        if user is None:
            print(f'Unknown User at row {idx}: {username}({username})')
            continue

        # Record
        coefficient = EventCoefficient.objects.get(
            campus_event=event,
            role=role
        )
        if attend:
            record = Record.objects.create(
                campus_event=event,
                user=user,
                status=Record.STATUS_FEEDBACK_REQUIRED,
                event_coefficient=coefficient,
            )
            PermissionService.assign_object_permissions(user, record)

def main():
    path = sys.argv[1]
    read_workload_content(
        row_parser=row_parser0,
        start_row=2,
        fpath=path,
    )

if __name__ == '__main__':
    with transaction.atomic():
        main()
