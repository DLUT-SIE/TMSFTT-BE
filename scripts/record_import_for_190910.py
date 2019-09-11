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

def row_parser0(row):
    return [row[2], row[4:10]]

def read_workload_content(
        row_parser=row_parser0, start_row=2,
        fpath='~/Desktop/TMSFTT/骨干教师教学能力提升培训班-考勤表-更新至第六场培训.xlsx'):
    '''Read xlsx file and generate records.'''
    workbook = xlrd.open_workbook(fpath)
    sheet = workbook.sheet_by_index(0)
    num_rows = sheet.nrows
    program = Program.objects.get(name='骨干教师教学能力提升培训班' )
    events = CampusEvent.objects.filter(program=program)
    users = {x.first_name: x for x in User.objects.all()}
    coefficients = {}
    for idx in tqdm(range(start_row, num_rows)):
        row = sheet.row_values(idx)
        try:
            (username, attends) = row_parser(row)
            role = EventCoefficient.ROLE_PARTICIPATOR
        except ValueError:
            print(idx, row)
            raise

        user = users.get(username, None) 
        if user is None:
            print(f'Unknown User at row {idx}: {username}({username})')
            continue

        # Record
        for i in range(5):
            coefficient_key = (events[i].id, role)
            if coefficient_key not in coefficients:
                coefficients[coefficient_key] = EventCoefficient.objects.get(
                    campus_event=events[i],
                    role=role
                )
            coefficient = coefficients[coefficient_key]
            if attends[i]:
                record = Record.objects.create(
                    campus_event=events[i],
                    user=user,
                    status=Record.STATUS_FEEDBACK_SUBMITTED,
                    event_coefficient=coefficient,
                )
                PermissionService.assign_object_permissions(user, record)

                #Feedback
                CampusEventFeedback.objects.create(record=record, content='import by admin')

        if attends[5]:
            record = Record.objects.create(
                campus_event=events[5],
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
