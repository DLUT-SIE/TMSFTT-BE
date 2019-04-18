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
        default_permissions = ()
        permissions = (
            ('add_campusevent', '允许添加校内培训活动'),
            ('view_campusevent', '允许查看校内培训活动'),
            ('change_campusevent', '允许修改校内培训活动'),
            ('delete_campusevent', '允许删除校内培训活动'),
        )

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
        default_permissions = ()
        permissions = (
            ('add_offcampusevent', '允许添加校外培训活动'),
            ('view_offcampusevent', '允许查看校外培训活动'),
            ('change_offcampusevent', '允许修改校外培训活动'),
            ('delete_offcampusevent', '允许删除校外培训活动'),
        )


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
        unique_together = (('campus_event', 'user'),)
        default_permissions = ()
        permissions = (
            ('add_enrollment', '允许添加活动报名记录'),
            ('view_enrollment', '允许查看活动报名记录'),
            ('change_enrollment', '允许修改活动报名记录'),
            ('delete_enrollment', '允许删除活动报名记录'),
        )

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


class EventCoefficient(models.Model):
    """EventCoefficient holds information about the coefficient of role
    in different event"""
    ROLE_PARTICIPATOR = 0
    ROLE_LECTURER = 1
    ROLE_JUDGE = 2
    ROLE_CHOICES = (
        (ROLE_PARTICIPATOR, _('参与教师')),
        (ROLE_LECTURER, _('主讲人')),
        (ROLE_JUDGE, _('评委')),
    )

    ROUND_METHOD_NONE = 0
    ROUND_METHOD_CEIL = 1
    ROUND_METHOD_FLOOR = 2
    ROUND_METHOD_DEFAULT = 3
    ROUND_CHOICES = (
        (ROUND_METHOD_NONE, _('正常计算')),
        (ROUND_METHOD_CEIL, _('向上取整')),
        (ROUND_METHOD_FLOOR, _('向下取整')),
        (ROUND_METHOD_DEFAULT, _('四舍五入')),
    )

    class Meta:
        verbose_name = _('培训活动系数')
        verbose_name_plural = _('培训活动系数')

    campus_event = models.ForeignKey(CampusEvent, verbose_name=_('校内培训活动'),
                                     blank=True, null=True,
                                     on_delete=models.PROTECT)
    off_campus_event = models.ForeignKey(OffCampusEvent,
                                         verbose_name=_('校外培训活动'),
                                         blank=True, null=True,
                                         on_delete=models.PROTECT)
    role = models.PositiveSmallIntegerField(verbose_name=_('参与角色'),
                                            choices=ROLE_CHOICES,
                                            default=ROLE_PARTICIPATOR)
    coefficient = models.FloatField(verbose_name=_('角色系数'), default=0.0)
    hours_option = models.PositiveSmallIntegerField(
        verbose_name=_('学时取整方式'), choices=ROUND_CHOICES,
        default=ROUND_METHOD_NONE)
    workload_option = models.PositiveSmallIntegerField(
        verbose_name=_('工作量取整方式'), choices=ROUND_CHOICES,
        default=ROUND_METHOD_NONE)
