'''Generate off campus event records from xlsx file.'''
# pylint: disable=wrong-import-position,ungrouped-imports,invalid-name
# pylint: disable=missing-docstring
import sys
import os
from datetime import datetime

import django

sys.path.insert(0, os.path.abspath('.'))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'TMSFTT.settings_dev')
django.setup()

from tqdm import tqdm
import xlrd
from django.db import transaction
from django.utils.timezone import make_aware

from auth.models import User
from auth.services import PermissionService
from infra.utils import prod_logger
from training_event.models import OffCampusEvent, EventCoefficient
from training_record.models import Record, RecordContent

def row_parser(row):
    return [row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8], row[9], row[10]]

def read_workload_content(
        row_parser=row_parser, start_row=2,
        fpath='~/Desktop/TMSFTT/教学工作坊-教学创新大赛.xlsx'):
    '''Read xlsx file and generate events&records.'''
    workbook = xlrd.open_workbook(fpath)
    sheet = workbook.sheet_by_index(0)
    num_rows = sheet.nrows

    for idx in tqdm(range(start_row, num_rows)):
        row = sheet.row_values(idx)
        try:
            (username, event_name, time, location,
             num_hours, num_participants, role, content,
             summary, feedback) = row_parser(row)
        except ValueError:
            print(idx, row)
            raise

        try:
            user = User.objects.get(username=str(int(username)))
        except Exception:
            print('学号为{}的老师不存在!'.format(username))
            raise

        role = 0 if role == '参与' else 1

        off_campus_event = {'name': event_name,
                            'time': make_aware(datetime.strptime(time, '%Y年%m月%d日')),
                            'location': location,
                            'num_hours': float(num_hours),
                            'num_participants': int(num_participants)}

        contents = [{'content_type': 0, 'content': content},
                    {'content_type': 1, 'content': summary},
                    {'content_type': 2, 'content': feedback}]

        with transaction.atomic():
            off_campus_event = OffCampusEvent.objects.create(
                **off_campus_event,
            )

            event_coefficient = EventCoefficient.objects.create(
                role=role, coefficient=0,
                off_campus_event=off_campus_event)

            record = Record.objects.create(
                off_campus_event=off_campus_event,
                user=user,
                event_coefficient=event_coefficient,
                status=Record.STATUS_SCHOOL_ADMIN_APPROVED
            )
            PermissionService.assign_object_permissions(user, record)

            for content in contents:
                record_content = RecordContent.objects.create(
                    record=record,
                    **content
                )
                PermissionService.assign_object_permissions(
                    user, record_content)

            msg = (f'管理员为用户{user}创建了其参加'
                   + f'{off_campus_event.name}'
                   + f'({off_campus_event.id})活动的培训记录')
            prod_logger.info(msg)
        idx = idx + 1

def main():
    path = sys.argv[1]
    read_workload_content(
        row_parser=row_parser,
        start_row=1,
        fpath=path,
    )

if __name__ == '__main__':
    with transaction.atomic():
        main()
