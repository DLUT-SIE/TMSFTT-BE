'''Define how our app behave under different configs.'''
from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class TrainingEventConfig(AppConfig):
    '''Basic config for our app.'''
    name = 'training_event'
    verbose_name = _('培训活动')
