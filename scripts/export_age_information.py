
'''export age information for a program'''
# pylint: disable=wrong-import-position,ungrouped-imports,invalid-name
# pylint: disable=missing-docstring
import sys
import os

import django

sys.path.insert(0, os.path.abspath('.'))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'TMSFTT.settings_dev')
django.setup()

from tqdm import tqdm
from django.db import transaction

from auth.models import User
from training_program.models import Program
from training_event.models import CampusEvent
from training_record.models import Record

program = Program.objects.get(name='午间教学沙龙')
events = CampusEvent.objects.filter(program=program).exclude(name='教学沙龙第十四期-助力青年教师教学创新发展')
ages = []
for event in events:
    records = Record.objects.filter(campus_event=event)
    for record in records:
        ages.append(record.user.age)
count = [0] *100
for age in ages:
    count[age-1] += 1
with open('a.txt', 'w') as f:
    for i in range(100):
        f.write('{}\t{}\n'.format(i+1, count[i]))
