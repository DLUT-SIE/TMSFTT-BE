'''Define ORM models for training_review module.'''
from django.contrib.auth import get_user_model
from django.db import models

from training_record.models import Record


User = get_user_model()


class ReviewNote(models.Model):
    '''ReviewNote provides notes from admin.

    Notes are created by admin to provide meaningful information to help
    users change their record during review.
    '''
    class Meta:
        verbose_name = '培训记录审核提示'
        verbose_name_plural = '培训记录审核提示'
        default_permissions = ()
        permissions = (
            ('add_reviewnote', '允许添加培训记录审核提示'),
            ('view_reviewnote', '允许查看培训记录审核提示'),
        )

    create_time = models.DateTimeField(verbose_name='创建时间',
                                       auto_now_add=True)
    record = models.ForeignKey(Record, verbose_name='培训记录',
                               on_delete=models.CASCADE)
    user = models.ForeignKey(User, verbose_name='创建用户',
                             on_delete=models.CASCADE)
    content = models.CharField(verbose_name='提示内容', max_length=128)

    def __str__(self):
        return '由{}创建的关于{}的审核提示'.format(self.user_id, self.record_id)
