from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class InfraConfig(AppConfig):
    name = 'infra'
    verbose_name = _('基础组件')
