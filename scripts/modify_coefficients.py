'''Modify coefficients of events in 2019 to 2'''
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
from datetime import datetime

from training_program.models import Program
from training_event.models import CampusEvent, EventCoefficient

def main():
    time = datetime.strptime('20190101', '%Y%m%d')
    programs = Program.objects.filter(id__in=(5, 8))
    events = CampusEvent.objects.filter(program__in=programs, time__gte=time)
    for event in tqdm(events):
        coefficients = EventCoefficient.objects.filter(campus_event=event)
        for coefficient in coefficients:
            if coefficient.role == 1:
                coefficient.coefficient = 2
                coefficient.save()

if __name__ == '__main__':
    with transaction.atomic():
        main()
