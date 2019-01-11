'''Define ORM models for training_program module.'''
from django.db import models
from django.utils.translation import gettext_lazy as _

from auth.models import Department


class ProgramCatgegory(models.Model):
    """Program category holds basic information about a category."""
    class Meta:
        verbose_name = _('培训类别')
        verbose_name_plural = _('培训类别')

    name = models.CharField(verbose_name=_('培训类别名称'), max_length=64)

    def __str__(self):
        return self.name


class ProgramForm(models.Model):
    """Program form defines the roles the user can be in a program."""
    class Meta:
        verbose_name = _('培训形式')
        verbose_name_plural = _('培训形式')

    name = models.CharField(verbose_name=_('培训形式名称'), max_length=64)

    def __str__(self):
        return self.name


class Program(models.Model):
    """Programs are managed by admins."""
    class Meta:
        verbose_name = _('培训项目')
        verbose_name_plural = _('培训项目')

    name = models.CharField(verbose_name=_('项目名称'), max_length=64)
    department = models.ForeignKey(Department, verbose_name=_('开设单位'),
                                   on_delete=models.PROTECT)
    category = models.ForeignKey(ProgramCatgegory, verbose_name=_('培训类别'),
                                 on_delete=models.PROTECT)
    form = models.ManyToManyField(ProgramForm, verbose_name=_('培训形式'),
                                  blank=True)

    def __str__(self):
        return self.name
