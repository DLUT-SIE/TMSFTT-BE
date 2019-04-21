'''Define how our app behave under different configs.'''
from django.apps import AppConfig


class InfraConfig(AppConfig):
    '''Basic config for our app.'''
    name = 'infra'
    verbose_name = '基础组件'
