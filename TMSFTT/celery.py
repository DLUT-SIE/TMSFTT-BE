'''Celery configurations.'''
import os

from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'TMSFTT.settings_prod')

app = Celery('TMSFTT')  # pylint: disable=invalid-name

app.config_from_object('django.conf:settings', namespace='CELERY')

app.autodiscover_tasks()
