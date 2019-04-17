'''Define ORM models for auth module.'''
from django.contrib.auth.models import Permission, AbstractUser, Group
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.utils.functional import cached_property


class Department(models.Model):
    '''Department holds public information related to department.

    Unlike Django's Group is used in permission checking, department is
    business-logic related, in most cases, we use this model to categorize
    other objects.
    '''
    class Meta:
        verbose_name = _('院系')
        verbose_name_plural = _('院系')
        default_permissions = ()
        permissions = (
            ('add_department', '允许添加学部学院'),
            ('view_department', '允许查看学部学院'),
            ('change_department', '允许修改学部学院'),
            ('delete_department', '允许删除学部学院'),
        )

    name = models.CharField(verbose_name=_('院系'), max_length=50, unique=True)
    create_time = models.DateTimeField(verbose_name=_('创建时间'),
                                       auto_now_add=True)
    update_time = models.DateTimeField(verbose_name=_('最近修改时间'),
                                       auto_now=True)

    def __str__(self):
        return str(self.name)


class Role(models.Model):
    '''Role objects connect User, Department and Group.

    The groups each user is in should be identical with the groups of the roles
    the user is. That said, if user is connected with N roles, then the user
    should at least be in N groups (extra groups are allowed since some of the
    groups are not related to roles, such as superadmin).

    NOTE: The ideal implementation would be that Group has a foreign key field
    to our department model, and it should have an extra field like role_type,
    then there is no need to keep this Role model, but since Group is created
    by Django, along with fully operational permission checking logic, so the
    Role model is required. But we need to make sure that the relation between
    user and groups should be removed when user switching from departments.
    '''
    class Meta:
        verbose_name = '身份'
        verbose_name_plural = '身份'
        default_permissions = ()
        permissions = (
            ('add_role', '允许添加身份'),
            ('view_role', '允许查看身份'),
            ('change_role', '允许修改身份'),
            ('delete_role', '允许删除身份'),
        )
        unique_together = (('department', 'role_type'),)

    ROLE_TEACHER = 1
    ROLE_DEPT_ADMIN = 2
    ROLE_CHOICES = (
        (ROLE_TEACHER, '专任教师'),
        (ROLE_DEPT_ADMIN, '院系管理员'),
    )

    role_type = models.PositiveSmallIntegerField(choices=ROLE_CHOICES)
    group = models.OneToOneField(
        Group, verbose_name=_('用户组'), on_delete=models.CASCADE)
    department = models.ForeignKey(
        Department, verbose_name=_('院系'), related_name='roles',
        on_delete=models.CASCADE)

    def __str__(self):
        return '{}({})'.format(self.department, self.get_role_type_display())


class User(AbstractUser):
    '''User holds private information for user.'''
    class Meta:
        verbose_name = _('用户')
        verbose_name_plural = _('用户')
        default_permissions = ()
        permissions = (
            ('add_user', '允许添加用户'),
            ('view_user', '允许查看用户'),
            ('change_user', '允许修改用户'),
            ('delete_user', '允许删除用户'),
        )

    department = models.ForeignKey(
        Department, verbose_name=_('所属学部学院'), on_delete=models.PROTECT,
        blank=True, null=True,
        related_name='users')
    roles = models.ManyToManyField(Role, related_name='users', blank=True)
    age = models.PositiveSmallIntegerField(verbose_name=_('年龄'), default=0)

    def __str__(self):
        return str(self.username)

    @cached_property
    def _roles(self):
        '''Retrieve the role types of the current user, and cache it.

        Return
        ------
        <QuerySet [{'role_type': 1}, {'role_type': 2}, {'role_type': 3}]>
        '''
        return self.roles.all().values('role_type')

    @property
    def is_teacher(self):
        '''Field to indicate whether the user is a teacher.'''
        return {'role_type': Role.ROLE_TEACHER} in self._roles

    @property
    def is_department_admin(self):
        '''Field to indicate whether the user is a department admin.'''
        return {'role_type': Role.ROLE_DEPT_ADMIN} in self._roles

    @property
    def is_school_admin(self):
        '''Field to indicate whether the user is a superadmin.'''
        return self.is_staff or self.is_superuser


class UserPermission(models.Model):
    '''A mapping to User-Permission Many-To-Many relationship.'''
    class Meta:
        verbose_name = _('用户权限')
        verbose_name_plural = _('用户权限')
        managed = False  # This model is managed by Django.
        db_table = 'tmsftt_auth_user_user_permissions'
        default_permissions = ()
        permissions = (
            ('add_userpermission', '允许添加用户权限'),
            ('view_userpermission', '允许查看用户权限'),
            ('change_userpermission', '允许修改用户权限'),
            ('delete_userpermission', '允许删除用户权限'),
        )

    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, verbose_name=_('用户'),
                             on_delete=models.CASCADE)
    permission = models.ForeignKey(Permission, verbose_name=_('权限'),
                                   on_delete=models.CASCADE)

    def __str__(self):
        return '用户{}拥有权限{}'.format(self.user_id, self.permission_id)


class GroupPermission(models.Model):
    '''A mapping to Group-Permission Many-To-Many relationship.'''
    class Meta:
        verbose_name = _('用户组权限')
        verbose_name_plural = _('用户组权限')
        managed = False  # This model is managed by Django.
        db_table = 'auth_group_permissions'
        default_permissions = ()
        permissions = (
            ('add_grouppermission', '允许添加用户组权限'),
            ('view_grouppermission', '允许查看用户组权限'),
            ('change_grouppermission', '允许修改用户组权限'),
            ('delete_grouppermission', '允许删除用户组权限'),
        )

    id = models.AutoField(primary_key=True)
    group = models.ForeignKey(Group, verbose_name=_('用户'),
                              on_delete=models.CASCADE)
    permission = models.ForeignKey(Permission, verbose_name=_('权限'),
                                   on_delete=models.CASCADE)

    def __str__(self):
        return '用户组{}拥有权限{}'.format(self.group_id, self.permission_id)
