'''Define how our app behave under different configs.'''
from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class InfraConfig(AppConfig):
    '''Basic config for our app.'''
    name = 'infra'
    verbose_name = _('基础组件')
