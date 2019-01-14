'''Define how our app behave under different configs.'''
from django.apps import AppConfig


class TrainingRecordConfig(AppConfig):
    '''Basic config for our app.'''
    name = 'training_record'
    verbose_name = _('培训记录')
