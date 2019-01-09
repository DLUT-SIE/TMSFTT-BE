from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class AuthConfig(AppConfig):
    name = 'auth'
    label = 'tmsftt_auth'
    verbose_name = _('权限')
