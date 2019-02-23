'''Define ORM models for training_event module.'''
from django.db import models
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _
from django.utils.text import format_lazy as _f

from training_program.models import Program


class AbstractEvent(models.Model):
    '''Abstract class for all events.'''
    class Meta:
        abstract = True

    create_time = models.DateTimeField(verbose_name=_('创建时间'),
                                       auto_now_add=True)
    update_time = models.DateTimeField(verbose_name=_('最近修改时间'),
                                       auto_now=True)
    name = models.CharField(verbose_name=_('活动名称'), max_length=64)
    time = models.DateTimeField(verbose_name=_('活动时间'))
    location = models.CharField(verbose_name=_('活动地点'), max_length=64)
    num_hours = models.FloatField(verbose_name=_('活动学时'))
    num_participants = models.PositiveIntegerField(verbose_name=_('活动人数'))

    def __str__(self):
        return self.name


class CampusEvent(AbstractEvent):
    '''Events that are held inside campus.'''
    class Meta(AbstractEvent.Meta):
        verbose_name = _('校内培训活动')
        verbose_name_plural = _('校内培训活动')

    program = models.ForeignKey(Program, verbose_name=_('培训项目'),
                                on_delete=models.PROTECT)
    deadline = models.DateTimeField(verbose_name=_('截止报名时间'))
    num_enrolled = models.PositiveSmallIntegerField(
        verbose_name=_('报名人数'), default=0)
    description = models.TextField(verbose_name=_('活动描述'), default='')


class OffCampusEvent(AbstractEvent):
    '''Events that are created by individual users.'''
    class Meta(AbstractEvent.Meta):
        verbose_name = _('校外培训活动')
        verbose_name_plural = _('校外培训活动')


class Enrollment(models.Model):
    '''Enrollment holds information about the event that the user enrolled.'''
    ENROLL_METHOD_WEB = 0
    ENROLL_METHOD_MOBILE = 1
    ENROLL_METHOD_QRCODE = 2
    ENROLL_METHOD_EMAIL = 3
    ENROLL_METHOD_IMPORT = 4
    ENROLL_METHOD_CHOICES = (
        (ENROLL_METHOD_WEB, _('网页报名')),
        (ENROLL_METHOD_MOBILE, _('移动端报名')),
        (ENROLL_METHOD_QRCODE, _('二维码报名')),
        (ENROLL_METHOD_EMAIL, _('邮件报名')),
        (ENROLL_METHOD_IMPORT, _('管理员导入')),
    )

    class Meta:
        verbose_name = _('活动报名记录')
        verbose_name_plural = _('活动报名记录')

    create_time = models.DateTimeField(verbose_name=_('创建时间'),
                                       auto_now_add=True)
    campus_event = models.ForeignKey(CampusEvent, verbose_name=_('校内活动'),
                                     on_delete=models.CASCADE)
    user = models.ForeignKey(get_user_model(), verbose_name=_('用户'),
                             on_delete=models.CASCADE)
    enroll_method = models.PositiveSmallIntegerField(
        verbose_name=_('报名渠道'), choices=ENROLL_METHOD_CHOICES,
        default=ENROLL_METHOD_WEB)
    is_participated = models.BooleanField(verbose_name=_('是否参加'),
                                          default=False)

    def __str__(self):
        return str(_f('{} 报名 {} 的记录', self.user_id, self.campus_event_id))
