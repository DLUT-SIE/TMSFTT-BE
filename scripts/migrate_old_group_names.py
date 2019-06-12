'''Migrate old group names to new style.'''
# pylint: disable=wrong-import-position,ungrouped-imports,invalid-name
# pylint: disable=missing-docstring
import logging
import sys
import os
import os.path as osp
import random
from datetime import datetime

import django

sys.path.insert(0, os.path.abspath('.'))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'TMSFTT.settings_dev')
django.setup()

from django.db import transaction
from django.contrib.auth.models import Group

from auth.models import Department


departments = Department.objects.all()
with transaction.atomic():
  for department in departments:
    groups = Group.objects.filter(name__startswith=f'{department.name}-')
    for group in groups:
      _, suffix = group.name.split('-')
      group.name = f'{department.name}-{department.raw_department_id}-{suffix}'
      group.save()
