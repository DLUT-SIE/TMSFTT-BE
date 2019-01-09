from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class TrainingProgramConfig(AppConfig):
    name = 'training_program'
    verbose_name = _('培训项目')
