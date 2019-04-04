'''Define ORM models for auth module.'''
from django.contrib.auth.models import Permission, AbstractUser, Group
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.utils.functional import cached_property


class User(AbstractUser):
    '''User holds private information for user.'''
    class Meta:
        verbose_name = _('用户')
        verbose_name_plural = _('用户')

    department = models.ForeignKey(
        'Department', verbose_name=_('所属学部学院'), on_delete=models.PROTECT,
        blank=True, null=True,
        related_name='users')
    roles = models.ManyToManyField('Role', related_name='users')
    age = models.PositiveSmallIntegerField(verbose_name=_('年龄'), default=0)

    def __str__(self):
        return str(self.username)

    @cached_property
    def _roles(self):
        '''Retrieve the role types of the current user, and cache it.

        Return
        ------
        <QuerySet [{'type': 1}, {'type': 2}, {'type': 3}]>
        '''
        return self.roles.all().values('type')

    @property
    def is_teacher(self):
        '''Field to indicate whether the user is a teacher.'''
        return {'type': Role.ROLE_TEACHER} in self._roles

    @property
    def is_dept_admin(self):
        '''Field to indicate whether the user is a department admin.'''
        return {'type': Role.ROLE_DEPT_ADMIN} in self._roles

    @property
    def is_superadmin(self):
        '''Field to indicate whether the user is a superadmin.'''
        return {'type': Role.ROLE_SUPERADMIN} in self._roles


class Role(models.Model):
    '''
    The Role entries are managed by the system, automatically created via a
    Django data migration.
    '''
    class Meta:
        verbose_name = '身份'
        verbose_name_plural = '身份'

    ROLE_TEACHER = 1
    ROLE_DEPT_ADMIN = 2
    # Superadmin is in business logic level, not a system level, so superadmin
    # still has no access to perform some critical operations.
    ROLE_SUPERADMIN = 3
    ROLE_CHOICES = (
        (ROLE_TEACHER, '专任教师'),
        (ROLE_DEPT_ADMIN, '部门管理员'),
        (ROLE_SUPERADMIN, '学校管理员'),
    )

    type = models.PositiveSmallIntegerField(choices=ROLE_CHOICES)

    def __str__(self):
        return self.get_type_display()


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
