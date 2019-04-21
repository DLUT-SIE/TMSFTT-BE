'''Define how our app behave under different configs.'''
from django.apps import AppConfig


class AuthConfig(AppConfig):
    '''Basic config for our app.'''
    name = 'auth'
    label = 'tmsftt_auth'
    verbose_name = '权限'
