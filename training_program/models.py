'''Define ORM models for training_program module.'''
from django.db import models

from auth.models import Department


class Program(models.Model):
    """Programs are managed by admins."""
    PROGRAM_CATEGORY_TRAINING = 1
    PROGRAM_CATEGORY_PROMOTION = 2
    PROGRAM_CATEGORY_TECHNOLOGY = 3
    PROGRAM_CATEGORY_HELP_CLASS = 4
    PROGRAM_CATEGORY_OTHERS = 5

    PROGRAM_CATEGORY_CHOICES = (
        (PROGRAM_CATEGORY_TRAINING, '教学培训'),
        (PROGRAM_CATEGORY_PROMOTION, '教学促进'),
        (PROGRAM_CATEGORY_TECHNOLOGY, '教学技术'),
        (PROGRAM_CATEGORY_HELP_CLASS, '青年教师助课'),
        (PROGRAM_CATEGORY_OTHERS, '其他'),
    )

    class Meta:
        verbose_name = '培训项目'
        verbose_name_plural = '培训项目'
        default_permissions = ()
        permissions = (
            ('add_program', '允许添加培训项目'),
            ('view_program', '允许查看培训项目'),
            ('change_program', '允许修改培训项目'),
            ('delete_program', '允许删除培训项目'),
        )

    name = models.CharField(verbose_name='项目名称', max_length=64)
    department = models.ForeignKey(Department, verbose_name='开设单位',
                                   on_delete=models.PROTECT)
    category = models.PositiveSmallIntegerField(verbose_name='培训类别',
                                                choices=(
                                                    PROGRAM_CATEGORY_CHOICES),
                                                default=(
                                                    PROGRAM_CATEGORY_OTHERS))

    def __str__(self):
        return self.name
