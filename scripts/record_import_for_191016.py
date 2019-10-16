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
    return [row[1], row[2], row[4]]

def read_workload_content(
        row_parser=row_parser0, start_row=2,
        fpath='~/Desktop/TMSFTT/教学工作坊-教学创新大赛.xlsx'):
    '''Read xlsx file and generate records.'''
    workbook = xlrd.open_workbook(fpath)
    program = Program.objects.get(name='教学工作坊')
    events = CampusEvent.objects.filter(program=program)
    try:
        event0 = events.filter(name='教学创新大赛专题培训工作坊')[0]
        event1 = events.filter(name='教学创新大赛专题培训工作坊 第二期')[0]
        event2 = events.filter(name='教学创新大赛专题培训工作坊 第三期')[0]
        event3 = events.filter(name='西浦大赛决赛直播观看工作坊')[0]
    except Exception:
        print('no event')
    events = [event0, event1, event2, event3]
    print(events)
    for i in range(4):
        sheet = workbook.sheet_by_index(i)
        num_rows = sheet.nrows
        event = events[i]

        for idx in tqdm(range(start_row, num_rows)):
            row = sheet.row_values(idx)
            try:
                (department_name, username, attend) = row_parser(row)
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

            role = (EventCoefficient.ROLE_EXPERT
                    if attend == 1 else EventCoefficient.ROLE_PARTICIPATOR)
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
        row_parser=row_parser0,
        start_row=1,
        fpath=path,
    )

if __name__ == '__main__':
    with transaction.atomic():
        main()
