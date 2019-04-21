<<<<<<< HEAD
# Generated by Django 2.1.5 on 2019-04-23 10:10
=======
# Generated by Django 2.1.5 on 2019-04-21 10:33
>>>>>>> make migration

import django.contrib.auth.models
import django.contrib.auth.validators
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0009_alter_user_last_name_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='GroupPermission',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
            ],
            options={
                'verbose_name': '用户组权限',
                'verbose_name_plural': '用户组权限',
                'db_table': 'auth_group_permissions',
                'permissions': (('add_grouppermission', '允许添加用户组权限'), ('view_grouppermission', '允许查看用户组权限'), ('change_grouppermission', '允许修改用户组权限'), ('delete_grouppermission', '允许删除用户组权限')),
                'managed': False,
                'default_permissions': (),
            },
        ),
        migrations.CreateModel(
            name='UserPermission',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
            ],
            options={
                'verbose_name': '用户权限',
                'verbose_name_plural': '用户权限',
                'db_table': 'tmsftt_auth_user_user_permissions',
                'permissions': (('add_userpermission', '允许添加用户权限'), ('view_userpermission', '允许查看用户权限'), ('change_userpermission', '允许修改用户权限'), ('delete_userpermission', '允许删除用户权限')),
                'managed': False,
                'default_permissions': (),
            },
        ),
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('username', models.CharField(error_messages={'unique': 'A user with that username already exists.'}, help_text='Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.', max_length=150, unique=True, validators=[django.contrib.auth.validators.UnicodeUsernameValidator()], verbose_name='username')),
                ('first_name', models.CharField(blank=True, max_length=30, verbose_name='first name')),
                ('last_name', models.CharField(blank=True, max_length=150, verbose_name='last name')),
                ('email', models.EmailField(blank=True, max_length=254, verbose_name='email address')),
                ('is_staff', models.BooleanField(default=False, help_text='Designates whether the user can log into this admin site.', verbose_name='staff status')),
                ('is_active', models.BooleanField(default=True, help_text='Designates whether this user should be treated as active. Unselect this instead of deleting accounts.', verbose_name='active')),
                ('date_joined', models.DateTimeField(default=django.utils.timezone.now, verbose_name='date joined')),
                ('gender', models.PositiveSmallIntegerField(choices=[(0, '未知'), (1, '男性'), (2, '女性'), (3, '未说明')], default=0, verbose_name='性别')),
                ('age', models.PositiveSmallIntegerField(default=0, verbose_name='年龄')),
                ('onboard_time', models.DateTimeField(blank=True, null=True, verbose_name='入校时间')),
                ('tenure_status', models.CharField(blank=True, max_length=40, null=True, verbose_name='任职状态')),
                ('education_background', models.CharField(blank=True, max_length=40, null=True, verbose_name='学历')),
                ('technical_title', models.CharField(blank=True, max_length=40, null=True, verbose_name='专业技术职称')),
                ('teaching_type', models.CharField(blank=True, max_length=40, null=True, verbose_name='任教类型')),
            ],
            options={
                'verbose_name': '用户',
                'verbose_name_plural': '用户',
                'permissions': (('add_user', '允许添加用户'), ('view_user', '允许查看用户'), ('change_user', '允许修改用户'), ('delete_user', '允许删除用户')),
                'default_permissions': (),
            },
            managers=[
                ('objects', django.contrib.auth.models.UserManager()),
            ],
        ),
        migrations.CreateModel(
            name='Department',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50, unique=True, verbose_name='院系')),
                ('create_time', models.DateTimeField(auto_now_add=True, verbose_name='创建时间')),
                ('update_time', models.DateTimeField(auto_now=True, verbose_name='最近修改时间')),
            ],
            options={
                'verbose_name': '院系',
                'verbose_name_plural': '院系',
                'permissions': (('add_department', '允许添加院系'), ('view_department', '允许查看院系'), ('change_department', '允许修改院系'), ('delete_department', '允许删除院系')),
                'default_permissions': (),
            },
        ),
        migrations.CreateModel(
            name='DepartmentInformation',
            fields=[
                ('dwid', models.CharField(db_column='DWID', max_length=20, primary_key=True, serialize=False, verbose_name='单位ID')),
                ('dwmc', models.CharField(blank=True, db_column='DWMC', max_length=100, null=True, verbose_name='单位名称')),
                ('dwfzr', models.CharField(blank=True, db_column='DWFZR', max_length=20, null=True, verbose_name='单位负责人')),
                ('dwjxfzr', models.CharField(blank=True, db_column='DWJXFRZ', max_length=20, null=True, verbose_name='单位教学负责人')),
                ('lsdw', models.CharField(blank=True, db_column='LSDW', max_length=20, null=True, verbose_name='隶属单位')),
                ('sfyx', models.CharField(blank=True, db_column='SFYX', max_length=1, null=True, verbose_name='是否有效')),
            ],
            options={
                'verbose_name': '单位基本信息',
                'verbose_name_plural': '单位基本信息',
                'db_table': 'TBL_DW_INFO',
                'ordering': ['dwid'],
                'default_permissions': (),
            },
        ),
        migrations.CreateModel(
            name='Role',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('role_type', models.PositiveSmallIntegerField(choices=[(1, '专任教师'), (2, '院系管理员')])),
                ('department', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='roles', to='tmsftt_auth.Department', verbose_name='院系')),
                ('group', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='auth.Group', verbose_name='用户组')),
            ],
            options={
                'verbose_name': '身份',
                'verbose_name_plural': '身份',
                'permissions': (('add_role', '允许添加身份'), ('view_role', '允许查看身份'), ('change_role', '允许修改身份'), ('delete_role', '允许删除身份')),
                'default_permissions': (),
            },
        ),

        migrations.CreateModel(
            name='TeacherInformation',
            fields=[
                ('zgh', models.CharField(db_column='ZGH', max_length=20, primary_key=True, serialize=False, verbose_name='职工号')),
                ('jsxm', models.CharField(blank=True, db_column='JSXM', max_length=100, null=True, verbose_name='教师姓名')),
                ('nl', models.CharField(blank=True, db_column='NL', max_length=10, null=True, verbose_name='年龄')),
                ('xb', models.CharField(blank=True, db_column='XB', max_length=10, null=True, verbose_name='性别')),
                ('xy', models.CharField(blank=True, db_column='XY', max_length=10, null=True, verbose_name='学院')),
                ('rxsj', models.CharField(blank=True, db_column='RXSJ', max_length=10, null=True, verbose_name='入校时间')),
                ('rzzt', models.CharField(blank=True, db_column='RZZT', max_length=40, null=True, verbose_name='任职状态')),
                ('xl', models.CharField(blank=True, db_column='XL', max_length=40, null=True, verbose_name='学历')),
                ('zyjszc', models.CharField(blank=True, db_column='ZYJSZC', max_length=40, null=True, verbose_name='专业技术职称')),
                ('rjlx', models.CharField(blank=True, db_column='RJLX', max_length=40, null=True, verbose_name='任教类型')),
            ],
            options={
                'verbose_name': '教师基本信息',
                'verbose_name_plural': '教师基本信息',
                'db_table': 'TBL_JB_INFO',
                'ordering': ['zgh'],
                'default_permissions': (),
            },
        ),
        migrations.AddField(
            model_name='user',
            name='department',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='users', to='tmsftt_auth.Department', verbose_name='所属院系'),
        ),
        migrations.AddField(
            model_name='user',
            name='groups',
            field=models.ManyToManyField(blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_name='user_set', related_query_name='user', to='auth.Group', verbose_name='groups'),
        ),
        migrations.AddField(
            model_name='user',
            name='roles',
            field=models.ManyToManyField(blank=True, related_name='users', to='tmsftt_auth.Role'),
        ),
        migrations.AddField(
            model_name='user',
            name='user_permissions',
            field=models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='user_set', related_query_name='user', to='auth.Permission', verbose_name='user permissions'),
        ),
        migrations.AlterUniqueTogether(
            name='role',
            unique_together={('department', 'role_type')},
        ),
    ]
