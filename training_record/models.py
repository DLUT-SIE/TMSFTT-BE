from django.contrib.auth.models import User
from django.db import models
from django.db.models.signals import pre_save
from django.utils.translation import gettext_lazy as _

from infra.models import OperationLog
from infra.utils import CustomHashPath
from training_program.models import Program


class Record(models.Model):
    '''Record records the attendance of users.'''
    STATUS_SUBMITTED = 0
    STATUS_FACULTY_ADMIN_REVIEWED = 1
    STATUS_SCHOOL_ADMIN_REVIEWED = 2
    STATUS_CHOICES = (
        (STATUS_SUBMITTED, _('已提交')),
        (STATUS_FACULTY_ADMIN_REVIEWED, _('院系管理员已审核')),
        (STATUS_SCHOOL_ADMIN_REVIEWED, _('学校管理员已审核')),
    )

    class Meta:
        verbose_name = _('培训记录')
        verbose_name_plural = _('培训记录')

    create_time = models.DateTimeField(verbose_name=_('创建时间'),
                                       auto_now_add=True)
    update_time = models.DateTimeField(verbose_name=_('最近修改时间'),
                                       auto_now=True)
    program_name = models.CharField(verbose_name=_('项目名称'),
                                    max_length=64, blank=True, null=True)
    program = models.ForeignKey(Program, verbose_name=_('培训项目'),
                                blank=True, null=True,
                                on_delete=models.PROTECT)
    time = models.DateTimeField(verbose_name=_('参加时间'))
    location = models.CharField(verbose_name=_('参加地点'), max_length=64)
    num_hours = models.FloatField(verbose_name=_('参加学时'))
    num_participants = models.PositiveIntegerField(verbose_name=_('参加人数'))
    user = models.ForeignKey(User, verbose_name=_('参加用户'),
                             on_delete=models.PROTECT)
    status = models.PositiveSmallIntegerField(verbose_name=_('当前状态'),
                                              choices=STATUS_CHOICES,
                                              default=STATUS_SUBMITTED)

    def __str__(self):
        return '{}({})'.format(self.user, self.program or self.program_name)

    @classmethod
    def check_program_set(cls, sender, instance, **kwargs):
        '''Check one and only one of program_name and program has been set.'''
        if instance.program_name and not instance.program:
            return
        elif not instance.program_name and instance.program:
            return
        raise ValueError(
            _('One and only one of program_name and program should be set.'))


# Connect to pre_save signal, so the check will happen before saving to db.
pre_save.connect(Record.check_program_set, sender=Record)


class RecordContent(models.Model):
    '''RecordContent stores text-like content for records.'''
    CONTENT_TYPE_CONTENT = 0
    CONTENT_TYPE_SUMMARY = 1
    CONTENT_TYPE_FEEDBACK = 2
    CONTENT_TYPE_CHOICES = (
        (CONTENT_TYPE_CONTENT, _('培训内容')),
        (CONTENT_TYPE_SUMMARY, _('培训总结')),
        (CONTENT_TYPE_FEEDBACK, _('培训反馈')),
    )

    class Meta:
        verbose_name = _('培训记录内容')
        verbose_name_plural = _('培训记录内容')

    create_time = models.DateTimeField(verbose_name=_('创建时间'),
                                       auto_now_add=True)
    update_time = models.DateTimeField(verbose_name=_('最近修改时间'),
                                       auto_now=True)
    record = models.ForeignKey(Record, verbose_name=_('培训记录'),
                               on_delete=models.CASCADE)
    content_type = models.PositiveSmallIntegerField(
        verbose_name=_('内容类型'), choices=CONTENT_TYPE_CHOICES)
    content = models.TextField(verbose_name=_('内容'))

    def __str__(self):
        return '{}({})'.format(self.get_content_type_display(), self.record)


class RecordAttachment(models.Model):
    '''RecordAttachment stores file-like content for records.'''
    ATTACHMENT_TYPE_CONTENT = 0
    ATTACHMENT_TYPE_SUMMARY = 1
    ATTACHMENT_TYPE_FEEDBACK = 2
    ATTACHMENT_TYPE_OTHERS = 3
    ATTACHMENT_TYPE_CHOICES = (
        (ATTACHMENT_TYPE_CONTENT, _('培训内容')),
        (ATTACHMENT_TYPE_SUMMARY, _('培训总结')),
        (ATTACHMENT_TYPE_FEEDBACK, _('培训反馈')),
        (ATTACHMENT_TYPE_OTHERS, _('其他附件')),
    )

    class Meta:
        verbose_name = _('培训记录附件')
        verbose_name_plural = _('培训记录附件')

    create_time = models.DateTimeField(verbose_name=_('创建时间'),
                                       auto_now_add=True)
    update_time = models.DateTimeField(verbose_name=_('最近修改时间'),
                                       auto_now=True)
    record = models.ForeignKey(Record, verbose_name=_('培训记录'),
                               on_delete=models.CASCADE)
    attachment_type = models.PositiveSmallIntegerField(
        verbose_name=_('附件类型'), choices=ATTACHMENT_TYPE_CHOICES)
    path = models.FileField(verbose_name=_('附件地址'),
                            upload_to=CustomHashPath('record_attachments'))

    def __str__(self):
        return '{}({})'.format(self.get_attachment_type_display(), self.record)


class StatusChangeLog(OperationLog):
    '''StatusChangeLog records the status change of the record instance.'''
    class Meta:
        verbose_name = _('培训及路状态更改日志')
        verbose_name_plural = _('培训及路状态更改日志')

    record = models.ForeignKey(Record, verbose_name=_('培训记录'),
                               on_delete=models.CASCADE)
    pre_status = models.PositiveSmallIntegerField(
        verbose_name=_('更改前状态'), choices=Record.STATUS_CHOICES,
        blank=True, null=True)
    post_status = models.PositiveSmallIntegerField(
        verbose_name=_('更改后状态'), choices=Record.STATUS_CHOICES,
        blank=True, null=True)
    description = models.CharField(verbose_name=_('状态更改描述信息'),
                                   max_length=64, blank=True, null=True)

    def __str__(self):
        return _('{}状态于{}由{}变为{}').format(
            self.record, self.time,
            self.get_pre_status_display(),
            self.get_post_status_display())
