'''Define ORM models for auth module.'''
from django.contrib.auth.models import Permission, AbstractUser, Group
from django.db import models
from django.utils.translation import gettext_lazy as _


class User(AbstractUser):
    '''User holds private information for user.'''
    class Meta:
        verbose_name = _('用户')
        verbose_name_plural = _('用户')

    update_time = models.DateTimeField(verbose_name=_('最近修改时间'),
                                       auto_now=True)
    department = models.ForeignKey(
        'Department', verbose_name=_('学部学院'), on_delete=models.PROTECT,
        blank=True, null=True,
        related_name='users')
    adminship_department = models.ForeignKey(
        'Department', verbose_name=_('管辖学部学院'), on_delete=models.PROTECT,
        blank=True, null=True, related_name='admins')
    age = models.PositiveSmallIntegerField(verbose_name=_('年龄'), default=0)

    def __str__(self):
        return str(self.username)


class Department(Group):
    '''Department holds public information related to department.'''
    class Meta:
        verbose_name = _('学部学院')
        verbose_name_plural = _('学部学院')

    create_time = models.DateTimeField(verbose_name=_('创建时间'),
                                       auto_now_add=True)
    update_time = models.DateTimeField(verbose_name=_('最近修改时间'),
                                       auto_now=True)

    def __str__(self):
        return str(self.name)


class UserPermission(models.Model):
    '''A mapping to User-Permission Many-To-Many relationship.'''
    class Meta:
        verbose_name = _('用户权限')
        verbose_name_plural = _('用户权限')
        managed = False  # This model is managed by Django.
        db_table = 'tmsftt_auth_user_user_permissions'

    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, verbose_name=_('用户'),
                             on_delete=models.CASCADE)
    permission = models.ForeignKey(Permission, verbose_name=_('权限'),
                                   on_delete=models.CASCADE)

    def __str__(self):
        return '用户{}拥有权限{}'.format(self.user_id, self.permission_id)
