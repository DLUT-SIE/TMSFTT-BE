'''Define ORM models for training_record module.'''
from django.contrib.auth import get_user_model
from django.db import models
from django.db.models.signals import pre_save

from training_event.models import CampusEvent, OffCampusEvent, EventCoefficient
from training_record.utils import infer_attachment_type


class Record(models.Model):
    '''Record records the attendance of users.'''
    STATUS_SUBMITTED = 1
    STATUS_DEPARTMENT_ADMIN_APPROVED = 2
    STATUS_SCHOOL_ADMIN_APPROVED = 3
    STATUS_FEEDBACK_REQUIRED = 4
    STATUS_FEEDBACK_SUBMITTED = 5
    STATUS_DEPARTMENT_ADMIN_REJECTED = 6
    STATUS_SCHOOL_ADMIN_REJECTED = 7
    STATUS_CLOSED = 8
    STATUS_CHOICES = (
        (STATUS_SUBMITTED, '已提交'),
        (STATUS_DEPARTMENT_ADMIN_APPROVED, '院系管理员审核通过'),
        (STATUS_SCHOOL_ADMIN_APPROVED, '学校管理员审核通过'),
        (STATUS_FEEDBACK_REQUIRED, '培训反馈待提交'),
        (STATUS_FEEDBACK_SUBMITTED, '培训反馈已提交'),
        (STATUS_DEPARTMENT_ADMIN_REJECTED, '院系管理员审核不通过'),
        (STATUS_SCHOOL_ADMIN_REJECTED, '学校管理员审核不通过'),
        (STATUS_CLOSED, '状态关闭')
    )

    class Meta:
        verbose_name = '培训记录'
        verbose_name_plural = '培训记录'
        default_permissions = ()
        permissions = (
            ('add_record', '允许添加培训记录'),
            ('view_record', '允许查看培训记录'),
            ('change_record', '允许修改培训记录'),
            ('delete_record', '允许删除培训记录'),
            ('review_record', '允许审核培训记录'),
        )

    create_time = models.DateTimeField(verbose_name='创建时间',
                                       auto_now_add=True)
    update_time = models.DateTimeField(verbose_name='最近修改时间',
                                       auto_now=True)
    campus_event = models.ForeignKey(CampusEvent, verbose_name='校内培训活动',
                                     blank=True, null=True,
                                     related_name='records',
                                     on_delete=models.PROTECT)
    off_campus_event = models.OneToOneField(
        OffCampusEvent, verbose_name='校外培训活动', blank=True, null=True,
        on_delete=models.CASCADE)
    user = models.ForeignKey(get_user_model(), verbose_name='参加用户',
                             on_delete=models.PROTECT)
    status = models.PositiveSmallIntegerField(verbose_name='当前状态',
                                              choices=STATUS_CHOICES,
                                              default=STATUS_SUBMITTED)
    event_coefficient = models.ForeignKey(EventCoefficient,
                                          verbose_name='培训活动系数',
                                          related_name='records',
                                          on_delete=models.CASCADE)

    def __str__(self):
        return '{}({})'.format(
            self.user_id, self.campus_event_id or self.off_campus_event_id)

    @classmethod
    def check_event_set(cls, sender, instance, **kwargs):
        '''Check campus_event or off_campus_event has been set.'''
        if bool(instance.campus_event) != bool(instance.off_campus_event):
            return
        raise ValueError('有且只有校内培训活动或校外培训活动字段应被设置!')


# Connect to pre_save signal, so the check will happen before saving to db.
pre_save.connect(Record.check_event_set, sender=Record)


class RecordContent(models.Model):
    '''RecordContent stores text-like content for records.'''
    CONTENT_TYPE_CONTENT = 0
    CONTENT_TYPE_SUMMARY = 1
    CONTENT_TYPE_FEEDBACK = 2
    CONTENT_TYPE_CHOICES = (
        (CONTENT_TYPE_CONTENT, '培训内容'),
        (CONTENT_TYPE_SUMMARY, '培训总结'),
        (CONTENT_TYPE_FEEDBACK, '培训反馈'),
    )

    class Meta:
        verbose_name = '培训记录内容'
        verbose_name_plural = '培训记录内容'
        default_permissions = ()
        permissions = (
            ('view_recordcontent', '允许查看培训记录内容'),
        )

    create_time = models.DateTimeField(verbose_name='创建时间',
                                       auto_now_add=True)
    update_time = models.DateTimeField(verbose_name='最近修改时间',
                                       auto_now=True)
    record = models.ForeignKey(Record, verbose_name='培训记录',
                               related_name='contents',
                               db_index=True,
                               on_delete=models.CASCADE)
    content_type = models.PositiveSmallIntegerField(
        verbose_name='内容类型', choices=CONTENT_TYPE_CHOICES)
    content = models.TextField(verbose_name='内容')

    def __str__(self):
        return '{}({})'.format(self.get_content_type_display(), self.record_id)


class RecordAttachment(models.Model):
    '''RecordAttachment stores file-like content for records.'''
    ATTACHMENT_TYPE_CONTENT = 0
    ATTACHMENT_TYPE_SUMMARY = 1
    ATTACHMENT_TYPE_FEEDBACK = 2
    ATTACHMENT_TYPE_OTHERS = 3
    ATTACHMENT_TYPE_NOTSET = 4
    ATTACHMENT_TYPE_CHOICES = (
        (ATTACHMENT_TYPE_CONTENT, '培训内容'),
        (ATTACHMENT_TYPE_SUMMARY, '培训总结'),
        (ATTACHMENT_TYPE_FEEDBACK, '培训反馈'),
        (ATTACHMENT_TYPE_OTHERS, '其他附件'),
    )

    class Meta:
        verbose_name = '培训记录附件'
        verbose_name_plural = '培训记录附件'
        default_permissions = ()
        permissions = (
            ('view_recordattachment', '允许查看培训记录附件'),
        )

    create_time = models.DateTimeField(verbose_name='创建时间',
                                       auto_now_add=True)
    update_time = models.DateTimeField(verbose_name='最近修改时间',
                                       auto_now=True)
    record = models.ForeignKey(Record, verbose_name='培训记录',
                               related_name='attachments',
                               db_index=True,
                               on_delete=models.CASCADE)
    attachment_type = models.PositiveSmallIntegerField(
        verbose_name='附件类型', choices=ATTACHMENT_TYPE_CHOICES,
        default=ATTACHMENT_TYPE_NOTSET)
    path = models.FileField(verbose_name='附件地址',
                            upload_to='uploads/%Y/%m/%d/record_attachments')

    def __str__(self):
        return '{}({})'.format(self.get_attachment_type_display(),
                               self.record_id)

    # pylint:disable=unused-argument
    @classmethod
    def infer_attachment_type(cls, sender, instance, **kwargs):
        '''Check campus_event or off_campus_event has been set.'''
        if instance.attachment_type == cls.ATTACHMENT_TYPE_NOTSET:
            instance.attachment_type = infer_attachment_type(
                instance.path.name)


# Infer attachment_type on save.
pre_save.connect(RecordAttachment.infer_attachment_type,
                 sender=RecordAttachment)


class StatusChangeLog(models.Model):
    '''StatusChangeLog records the status change of the record instance.'''
    class Meta:
        verbose_name = '培训记录状态更改日志'
        verbose_name_plural = '培训记录状态更改日志'
        default_permissions = ()

    record = models.ForeignKey(Record, verbose_name='培训记录',
                               on_delete=models.CASCADE)
    pre_status = models.PositiveSmallIntegerField(
        verbose_name='更改前状态', choices=Record.STATUS_CHOICES,
        blank=True, null=True)
    post_status = models.PositiveSmallIntegerField(
        verbose_name='更改后状态', choices=Record.STATUS_CHOICES,
        blank=True, null=True)
    time = models.DateTimeField(verbose_name='更改时间')
    user = models.ForeignKey(get_user_model(), verbose_name='操作用户',
                             on_delete=models.PROTECT)

    def __str__(self):
        return '{}状态于{}由{}变为{}'.format(
            self.record_id, self.time, self.get_pre_status_display(),
            self.get_post_status_display())


class CampusEventFeedback(models.Model):
    '''CampusEventFeedback stores text-like feedback for records.'''
    class Meta:
        verbose_name = '培训活动反馈'
        verbose_name_plural = '培训活动反馈'
        default_permissions = ()
        permissions = (
            ('add_campuseventfeedback', '允许增加培训活动反馈'),
        )

    create_time = models.DateTimeField(verbose_name='创建时间',
                                       auto_now_add=True)
    record = models.OneToOneField(Record, verbose_name='培训记录',
                                  related_name='feedback',
                                  on_delete=models.CASCADE)
    content = models.CharField(verbose_name='反馈内容', max_length=120)

    def __str__(self):
        return '反馈内容({})'.format(self.record_id)
