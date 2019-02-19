'''Define ORM models for auth module.'''
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from django.db import models
from django.utils.translation import gettext_lazy as _


User = get_user_model()


class Department(models.Model):
    '''Department holds public information related to department.'''
    class Meta:
        verbose_name = _('学部学院信息')
        verbose_name_plural = _('学部学院信息')

    create_time = models.DateTimeField(verbose_name=_('创建时间'),
                                       auto_now_add=True)
    update_time = models.DateTimeField(verbose_name=_('最近修改时间'),
                                       auto_now=True)
    name = models.CharField(verbose_name=_('学部学院名'), max_length=64)
    # Many-To-Many relationship, holds information about department admins.
    admins = models.ManyToManyField(
        get_user_model(), verbose_name=_('管理员列表'), blank=True)

    def __str__(self):
        return str(self.name)


class UserProfile(models.Model):
    '''UserProfile contains additional information related to user.'''
    class Meta:
        verbose_name = _('用户信息')
        verbose_name_plural = _('用户信息')

    create_time = models.DateTimeField(verbose_name=_('创建时间'),
                                       auto_now_add=True)
    update_time = models.DateTimeField(verbose_name=_('最近修改时间'),
                                       auto_now=True)
    user = models.OneToOneField(User, verbose_name=_('帐户'),
                                on_delete=models.CASCADE)
    department = models.ForeignKey(Department, verbose_name=_('学部学院'),
                                   on_delete=models.PROTECT)
    age = models.PositiveSmallIntegerField(verbose_name=_('年龄'), default=0)

    def __str__(self):
        return str(self.user)


class UserPermission(models.Model):
    '''A mapping to User-Permission Many-To-Many relationship.'''
    class Meta:
        verbose_name = _('用户权限')
        verbose_name_plural = _('用户权限')
        managed = False  # This model is managed by Django.
        db_table = 'auth_user_user_permissions'

    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, verbose_name=_('用户'),
                             on_delete=models.CASCADE)
    permission = models.ForeignKey(Permission, verbose_name=_('权限'),
                                   on_delete=models.CASCADE)

    def __str__(self):
        return '用户{}拥有权限{}'.format(self.user_id, self.permission_id)
