'''Define ORM models for training_event module.'''
import math

from django.db import models
from django.contrib.auth import get_user_model

from training_program.models import Program


class AbstractEvent(models.Model):
    '''Abstract class for all events.'''
    class Meta:
        abstract = True

    create_time = models.DateTimeField(verbose_name='创建时间',
                                       auto_now_add=True)
    update_time = models.DateTimeField(verbose_name='最近修改时间',
                                       auto_now=True)
    name = models.CharField(verbose_name='活动名称', max_length=64)
    time = models.DateTimeField(verbose_name='活动时间')
    location = models.CharField(verbose_name='活动地点', max_length=64)
    num_hours = models.FloatField(verbose_name='活动学时')
    num_participants = models.PositiveIntegerField(verbose_name='活动人数')

    def __str__(self):
        return self.name


class CampusEvent(AbstractEvent):
    '''Events that are held inside campus.'''
    class Meta(AbstractEvent.Meta):
        verbose_name = '校内培训活动'
        verbose_name_plural = '校内培训活动'
        default_permissions = ()
        permissions = (
            ('add_campusevent', '允许添加校内培训活动'),
            ('view_campusevent', '允许查看校内培训活动'),
            ('change_campusevent', '允许修改校内培训活动'),
            ('delete_campusevent', '允许删除校内培训活动'),
            ('review_campusevent', '允许审核校内培训活动'),
        )

    program = models.ForeignKey(Program, verbose_name='培训项目',
                                on_delete=models.PROTECT)
    deadline = models.DateTimeField(verbose_name='截止报名时间')
    num_enrolled = models.PositiveSmallIntegerField(
        verbose_name='报名人数', default=0)
    description = models.TextField(verbose_name='活动描述', default='')
    reviewed = models.BooleanField(
        verbose_name='是否已由校级管理员审核确认', default=False)


class OffCampusEvent(AbstractEvent):
    '''Events that are created by individual users.'''
    class Meta(AbstractEvent.Meta):
        verbose_name = '校外培训活动'
        verbose_name_plural = '校外培训活动'
        default_permissions = ()


class Enrollment(models.Model):
    '''Enrollment holds information about the event that the user enrolled.'''
    ENROLL_METHOD_WEB = 0
    ENROLL_METHOD_MOBILE = 1
    ENROLL_METHOD_QRCODE = 2
    ENROLL_METHOD_EMAIL = 3
    ENROLL_METHOD_IMPORT = 4
    ENROLL_METHOD_CHOICES = (
        (ENROLL_METHOD_WEB, '网页报名'),
        (ENROLL_METHOD_MOBILE, '移动端报名'),
        (ENROLL_METHOD_QRCODE, '二维码报名'),
        (ENROLL_METHOD_EMAIL, '邮件报名'),
        (ENROLL_METHOD_IMPORT, '管理员导入'),
    )

    class Meta:
        verbose_name = '活动报名记录'
        verbose_name_plural = '活动报名记录'
        unique_together = (('campus_event', 'user'),)
        default_permissions = ()
        permissions = (
            ('add_enrollment', '允许添加活动报名记录'),
            ('delete_enrollment', '允许删除活动报名记录'),
        )

    create_time = models.DateTimeField(verbose_name='创建时间',
                                       auto_now_add=True)
    campus_event = models.ForeignKey(CampusEvent, verbose_name='校内活动',
                                     on_delete=models.CASCADE)
    user = models.ForeignKey(get_user_model(), verbose_name='用户',
                             on_delete=models.CASCADE)
    enroll_method = models.PositiveSmallIntegerField(
        verbose_name='报名渠道', choices=ENROLL_METHOD_CHOICES,
        default=ENROLL_METHOD_WEB)

    def __str__(self):
        return '{} 报名 {} 的记录'.format(self.user_id, self.campus_event_id)


class EventCoefficient(models.Model):
    """
    EventCoefficient holds information about the coefficient of role
    in different event"""
    ROLE_PARTICIPATOR = 0
    ROLE_EXPERT = 1
    ROLE_CHOICES = (
        (ROLE_PARTICIPATOR, '参与'),
        (ROLE_EXPERT, '专家'),
    )
    ROLE_CHOICES_MAP = {v: k for k, v in ROLE_CHOICES}

    ROUND_METHOD_NONE = 0
    ROUND_METHOD_CEIL = 1
    ROUND_METHOD_FLOOR = 2
    ROUND_METHOD_DEFAULT = 3
    ROUND_CHOICES = (
        (ROUND_METHOD_NONE, '正常计算'),
        (ROUND_METHOD_CEIL, '向上取整'),
        (ROUND_METHOD_FLOOR, '向下取整'),
        (ROUND_METHOD_DEFAULT, '四舍五入'),
    )

    class Meta:
        verbose_name = '培训活动系数'
        verbose_name_plural = '培训活动系数'
        default_permissions = ()
        unique_together = (
            ('campus_event', 'role'),
            ('off_campus_event', 'role'),
        )

    campus_event = models.ForeignKey(CampusEvent, verbose_name='校内培训活动',
                                     blank=True, null=True,
                                     on_delete=models.PROTECT)
    off_campus_event = models.ForeignKey(OffCampusEvent,
                                         verbose_name='校外培训活动',
                                         blank=True, null=True,
                                         on_delete=models.PROTECT)
    role = models.PositiveSmallIntegerField(verbose_name='参与角色',
                                            choices=ROLE_CHOICES,
                                            default=ROLE_PARTICIPATOR)
    coefficient = models.FloatField(verbose_name='角色系数', default=0.0)
    hours_option = models.PositiveSmallIntegerField(
        verbose_name='学时取整方式', choices=ROUND_CHOICES,
        default=ROUND_METHOD_NONE)
    workload_option = models.PositiveSmallIntegerField(
        verbose_name='工作量取整方式', choices=ROUND_CHOICES,
        default=ROUND_METHOD_NONE)

    def calculate_campus_event_workload(self, record):
        '''calculate wordkload by record'''
        # calculate campus_event num_hours based on  hours_option
        hour = self._round(record.campus_event.num_hours, self.hours_option)

        # calculate workload based on workload_option
        default_workload = hour * self.coefficient
        return self._round(default_workload, self.workload_option)

    def calculate_off_campus_event_workload(
            self, record):  # pylint: disable=unused-argument
        ''' to be confirmed someday'''
        return 0

    def calculate_event_workload(self, record):
        '''calculate event workload by event type'''
        if record.campus_event:
            return self.calculate_campus_event_workload(record)
        return self.calculate_off_campus_event_workload(record)

    @classmethod
    def _round(cls, value, option):
        if option == cls.ROUND_METHOD_CEIL:
            return math.ceil(value)
        if option == EventCoefficient.ROUND_METHOD_FLOOR:
            return math.floor(value)
        if option == EventCoefficient.ROUND_METHOD_DEFAULT:
            return round(value)
        return value
