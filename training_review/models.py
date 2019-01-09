from django.contrib.auth.models import User
from django.db import models
from django.utils.translation import gettext_lazy as _

from training_record.models import Record


class ReviewNote(models.Model):
    '''ReviewNote provides notes from admin.

    Notes are created by admin to provide meaningful information to help
    users change their record during review.
    '''
    class Meta:
        verbose_name = _('培训记录审核提示')
        verbose_name_plural = _('培训记录审核提示')

    create_time = models.DateTimeField(verbose_name=_('创建时间'),
                                       auto_now_add=True)
    record = models.ForeignKey(Record, verbose_name=_('培训记录'),
                               on_delete=models.CASCADE)
    field_name = models.CharField(verbose_name=_('字段名称'), max_length=32)
    user = models.ForeignKey(User, verbose_name=_('创建用户'),
                             on_delete=models.CASCADE)
    content = models.CharField(verbose_name=_('提示内容'), max_length=128)

    def __str__(self):
        return _('由{}创建的关于{}的审核提示').format(
            self.user, self.record)
