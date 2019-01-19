'''Define ORM models for training_record module.'''
from django.contrib.auth import get_user_model
from django.db import models
from django.db.models.signals import pre_save
from django.utils.translation import gettext_lazy as _
from django.utils.text import format_lazy as _f

from training_event.models import CampusEvent, OffCampusEvent


class Record(models.Model):
    '''Record records the attendance of users.'''
    STATUS_PRESUBMIT = 0
    STATUS_SUBMITTED = 1
    STATUS_FACULTY_ADMIN_REVIEWED = 2
    STATUS_SCHOOL_ADMIN_REVIEWED = 3
    STATUS_CHOICES = (
        (STATUS_PRESUBMIT, _('预提交')),
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
    campus_event = models.ForeignKey(CampusEvent, verbose_name=_('校内培训活动'),
                                     blank=True, null=True,
                                     related_name='campus_event',
                                     on_delete=models.PROTECT)
    off_campus_event = models.OneToOneField(
        OffCampusEvent, verbose_name=_('校外培训活动'), blank=True, null=True,
        on_delete=models.CASCADE)
    user = models.ForeignKey(get_user_model(), verbose_name=_('参加用户'),
                             on_delete=models.PROTECT)
    status = models.PositiveSmallIntegerField(verbose_name=_('当前状态'),
                                              choices=STATUS_CHOICES,
                                              default=STATUS_SUBMITTED)

    def __str__(self):
        return '{}({})'.format(self.user,
                               self.campus_event or self.off_campus_event)

    @classmethod
    def check_event_set(cls, sender, instance, **kwargs):
        '''Check campus_event or off_campus_event has been set.'''
        if bool(instance.campus_event) != bool(instance.off_campus_event):
            return
        raise ValueError(_('有且只有校内培训活动或校外培训活动字段应被设置!'))


# Connect to pre_save signal, so the check will happen before saving to db.
pre_save.connect(Record.check_event_set, sender=Record)


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
        verbose_name=_('附件类型'), choices=ATTACHMENT_TYPE_CHOICES,
        default=ATTACHMENT_TYPE_OTHERS)
    path = models.FileField(verbose_name=_('附件地址'),
                            upload_to='uploads/%Y/%m/%d/record_attachments')

    def __str__(self):
        return '{}({})'.format(self.get_attachment_type_display(), self.record)


class StatusChangeLog(models.Model):
    '''StatusChangeLog records the status change of the record instance.'''
    class Meta:
        verbose_name = _('培训记录状态更改日志')
        verbose_name_plural = _('培训记录状态更改日志')

    record = models.ForeignKey(Record, verbose_name=_('培训记录'),
                               on_delete=models.CASCADE)
    pre_status = models.PositiveSmallIntegerField(
        verbose_name=_('更改前状态'), choices=Record.STATUS_CHOICES,
        blank=True, null=True)
    post_status = models.PositiveSmallIntegerField(
        verbose_name=_('更改后状态'), choices=Record.STATUS_CHOICES,
        blank=True, null=True)
    time = models.DateTimeField(verbose_name=_('更改时间'))
    user = models.ForeignKey(get_user_model(), verbose_name=_('操作用户'),
                             on_delete=models.PROTECT)

    def __str__(self):
        return str(_f('{}状态于{}由{}变为{}', self.record, self.time,
                      self.get_pre_status_display(),
                      self.get_post_status_display()))
