'''Define ORM models for auth module.'''
from django.contrib.auth.models import Permission, AbstractUser, Group
from django.db import models

from auth.services import (
    EducationBackgroundConverter,
    TechnicalTitleConverter,
    GenderConverter,
    TenureStatusConverter,
    TeachingTypeConverter
)


class Department(models.Model):
    '''Department holds public information related to department.

    Unlike Django's Group is used in permission checking, department is
    business-logic related, in most cases, we use this model to categorize
    other objects.
    '''
    class Meta:
        verbose_name = '院系'
        verbose_name_plural = '院系'
        default_permissions = ()
        permissions = (
            ('add_department', '允许添加院系'),
            ('view_department', '允许查看院系'),
            ('change_department', '允许修改院系'),
            ('delete_department', '允许删除院系'),
        )

    raw_department_id = models.CharField(
        verbose_name='单位原始ID', max_length=20, unique=True)
    name = models.CharField(verbose_name='院系', max_length=50, unique=True)
    super_department = models.ForeignKey(
        'self', verbose_name='所属机构', blank=True, null=True,
        related_name='child_department', on_delete=models.PROTECT)
    create_time = models.DateTimeField(verbose_name='创建时间',
                                       auto_now_add=True)
    update_time = models.DateTimeField(verbose_name='最近修改时间',
                                       auto_now=True)

    def __str__(self):
        return str(self.name)


class User(AbstractUser):
    '''User holds private information for user.'''
    GENDER_UNKNOWN = 0
    GENDER_MALE = 1
    GENDER_FEMALE = 2
    GENDER_PRIVATE = 3
    GENDER_CHOICES = (
        (GENDER_UNKNOWN, '未知'),
        (GENDER_MALE, '男性'),
        (GENDER_FEMALE, '女性'),
        (GENDER_PRIVATE, '未说明'),
    )
    GENDER_CHOICES_MAP = {label: key for key, label in GENDER_CHOICES}

    class Meta:
        verbose_name = '用户'
        verbose_name_plural = '用户'
        default_permissions = ()
        permissions = (
            ('add_user', '允许添加用户'),
            ('view_user', '允许查看用户'),
            ('change_user', '允许修改用户'),
            ('delete_user', '允许删除用户'),
        )

    department = models.ForeignKey(
        Department, verbose_name='所属院系', on_delete=models.PROTECT,
        blank=True, null=True,
        related_name='users')
    gender = models.PositiveSmallIntegerField(
        verbose_name='性别', choices=GENDER_CHOICES, default=GENDER_UNKNOWN,
    )
    age = models.PositiveSmallIntegerField(verbose_name='年龄', default=0)
    onboard_time = models.DateTimeField(
        verbose_name='入校时间', blank=True, null=True)
    tenure_status = models.CharField(
        verbose_name='任职状态', max_length=40, blank=True, null=True)
    education_background = models.CharField(
        verbose_name='学历', max_length=40, blank=True, null=True)
    technical_title = models.CharField(
        verbose_name='专业技术职称', max_length=40, blank=True, null=True)
    teaching_type = models.CharField(
        verbose_name='任教类型', max_length=40, blank=True, null=True)

    def __str__(self):
        return self.username

    @property
    def is_teacher(self):
        '''Field to indicate whether the user is a teacher.'''
        return self.groups.filter(name__endswith='专任教师').exists()

    @property
    def is_department_admin(self):
        '''Field to indicate whether the user is a department admin.'''
        return self.groups.filter(name__endswith='管理员').exists()

    @property
    def is_school_admin(self):
        '''Field to indicate whether the user is a superadmin.'''
        return self.is_staff or self.is_superuser or self.groups.filter(
            name='大连理工大学-管理员').exists()


class UserGroup(models.Model):
    '''A mapping to User-Group Many-To-Many relationship.'''
    class Meta:
        verbose_name = '用户组'
        verbose_name_plural = '用户组'
        managed = False  # This model is managed by Django.
        db_table = 'tmsftt_auth_user_groups'
        default_permissions = ()

    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, verbose_name='用户',
                             on_delete=models.CASCADE)
    group = models.ForeignKey(Group, verbose_name='用户组',
                              on_delete=models.CASCADE)

    def __str__(self):
        return '用户{}位于用户组{}中'.format(self.user_id, self.group_id)


class UserPermission(models.Model):
    '''A mapping to User-Permission Many-To-Many relationship.'''
    class Meta:
        verbose_name = '用户权限'
        verbose_name_plural = '用户权限'
        managed = False  # This model is managed by Django.
        db_table = 'tmsftt_auth_user_user_permissions'
        default_permissions = ()

    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, verbose_name='用户',
                             on_delete=models.CASCADE)
    permission = models.ForeignKey(Permission, verbose_name='权限',
                                   on_delete=models.CASCADE)

    def __str__(self):
        return '用户{}拥有权限{}'.format(self.user_id, self.permission_id)


class GroupPermission(models.Model):
    '''A mapping to Group-Permission Many-To-Many relationship.'''
    class Meta:
        verbose_name = '用户组权限'
        verbose_name_plural = '用户组权限'
        managed = False  # This model is managed by Django.
        db_table = 'auth_group_permissions'
        default_permissions = ()

    id = models.AutoField(primary_key=True)
    group = models.ForeignKey(Group, verbose_name='用户组',
                              on_delete=models.CASCADE)
    permission = models.ForeignKey(Permission, verbose_name='权限',
                                   on_delete=models.CASCADE)

    def __str__(self):
        return '用户组{}拥有权限{}'.format(self.group_id, self.permission_id)


class TeacherInformation(models.Model):
    '''Raw data of teacher information.

    From our backend's view, this table is READ-ONLY. Its data is maintained
    by DLUT-ITS.
    '''
    class Meta:
        verbose_name = '教师基本信息'
        verbose_name_plural = '教师基本信息'
        db_table = 'TBL_JB_INFO'
        default_permissions = ()
        ordering = ['zgh']

    zgh = models.CharField(verbose_name='职工号', max_length=20,
                           db_column='ZGH', primary_key=True)
    jsxm = models.CharField(verbose_name='教师姓名', max_length=100,
                            db_column='JSXM', blank=True, null=True)
    nl = models.CharField(verbose_name='年龄', max_length=10,
                          db_column='NL', blank=True, null=True)
    xb = models.CharField(verbose_name='性别', max_length=10,
                          db_column='XB', blank=True, null=True)
    xy = models.CharField(verbose_name='学院', max_length=10,
                          db_column='XY', blank=True, null=True)
    rxsj = models.CharField(verbose_name='入校时间', max_length=10,
                            db_column='RXSJ', blank=True, null=True)
    rzzt = models.CharField(verbose_name='任职状态', max_length=40,
                            db_column='RZZT', blank=True, null=True)
    xl = models.CharField(verbose_name='学历', max_length=40,
                          db_column='XL', blank=True, null=True)
    zyjszc = models.CharField(verbose_name='专业技术职称', max_length=40,
                              db_column='ZYJSZC', blank=True, null=True)
    rjlx = models.CharField(verbose_name='任教类型', max_length=40,
                            db_column='RJLX', blank=True, null=True)

    def save(self, *args, **kwargs):
        raise Exception('该表状态为只读')

    def delete(self, *args, **kwargs):
        raise Exception('该表状态为只读')

    def get_xl_display(self):
        '''Return human-readable value of xl field.'''
        return EducationBackgroundConverter.get_value(self.xl)

    def get_zyjszc_display(self):
        '''Return human-readable value of zyjszc field.'''
        return TechnicalTitleConverter.get_value(self.zyjszc)

    def get_xb_display(self):
        '''Return human-readable value of xb field.'''
        return GenderConverter.get_value(self.xb)

    def get_rzzt_display(self):
        '''Return human-readable value of rzzt field.'''
        return TenureStatusConverter.get_value(self.rzzt)

    def get_rjlx_display(self):
        '''Return human-readable value of rjlx field.'''
        return TeachingTypeConverter.get_value(self.rjlx)


class DepartmentInformation(models.Model):
    '''Raw data of department information.

    From our backend's view, this table is READ-ONLY. Its data is maintained
    by DLUT-ITS.
    '''
    class Meta:
        verbose_name = '单位基本信息'
        verbose_name_plural = '单位基本信息'
        db_table = 'TBL_DW_INFO'
        default_permissions = ()
        ordering = ['dwid']

    dwid = models.CharField(verbose_name='单位ID', max_length=20,
                            db_column='DWID', primary_key=True)
    dwmc = models.CharField(verbose_name='单位名称', max_length=100,
                            db_column='DWMC', blank=True, null=True)
    dwfzr = models.CharField(verbose_name='单位负责人', max_length=20,
                             db_column='DWFZR', blank=True, null=True)
    dwjxfzr = models.CharField(verbose_name='单位教学负责人', max_length=20,
                               db_column='DWJXFRZ', blank=True, null=True)
    lsdw = models.CharField(verbose_name='隶属单位', max_length=20,
                            db_column='LSDW', blank=True, null=True)
    sfyx = models.CharField(verbose_name='是否有效', max_length=1,
                            db_column='SFYX', blank=True, null=True)

    def save(self, *args, **kwargs):
        raise Exception('该表状态为只读')

    def delete(self, *args, **kwargs):
        raise Exception('该表状态为只读')
