'''Define how our app behave under different configs.'''
from django.apps import AppConfig


class TrainingEventConfig(AppConfig):
    '''Basic config for our app.'''
    name = 'training_event'
    verbose_name = '培训活动'
