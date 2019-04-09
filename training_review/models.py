'''Define ORM models for training_review module.'''
from django.contrib.auth import get_user_model
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.utils.text import format_lazy as _f

from training_record.models import Record


User = get_user_model()


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
    user = models.ForeignKey(User, verbose_name=_('创建用户'),
                             on_delete=models.CASCADE)
    content = models.CharField(verbose_name=_('提示内容'), max_length=128)

    def __str__(self):
        return str(_f('由{}创建的关于{}的审核提示', self.user_id, self.record_id))
