'''Define how our app behave under different configs.'''
from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class AuthConfig(AppConfig):
    '''Basic config for our app.'''
    name = 'auth'
    label = 'tmsftt_auth'
    verbose_name = _('权限')
