# Generated by Django 2.1.5 on 2019-01-13 06:41

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import infra.utils


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('training_event', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Record',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('create_time', models.DateTimeField(auto_now_add=True, verbose_name='创建时间')),
                ('update_time', models.DateTimeField(auto_now=True, verbose_name='最近修改时间')),
                ('status', models.PositiveSmallIntegerField(choices=[(0, '已提交'), (1, '院系管理员已审核'), (2, '学校管理员已审核')], default=0, verbose_name='当前状态')),
                ('campus_event', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='campus_event', to='training_event.CampusEvent', verbose_name='校内培训活动')),
                ('off_campus_event', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='training_event.OffCampusEvent', verbose_name='校外培训活动')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to=settings.AUTH_USER_MODEL, verbose_name='参加用户')),
            ],
            options={
                'verbose_name': '培训记录',
                'verbose_name_plural': '培训记录',
            },
        ),
        migrations.CreateModel(
            name='RecordAttachment',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('create_time', models.DateTimeField(auto_now_add=True, verbose_name='创建时间')),
                ('update_time', models.DateTimeField(auto_now=True, verbose_name='最近修改时间')),
                ('attachment_type', models.PositiveSmallIntegerField(choices=[(0, '培训内容'), (1, '培训总结'), (2, '培训反馈'), (3, '其他附件')], verbose_name='附件类型')),
                ('path', models.FileField(upload_to=infra.utils.CustomHashPath('record_attachments'), verbose_name='附件地址')),
                ('record', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='training_record.Record', verbose_name='培训记录')),
            ],
            options={
                'verbose_name': '培训记录附件',
                'verbose_name_plural': '培训记录附件',
            },
        ),
        migrations.CreateModel(
            name='RecordContent',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('create_time', models.DateTimeField(auto_now_add=True, verbose_name='创建时间')),
                ('update_time', models.DateTimeField(auto_now=True, verbose_name='最近修改时间')),
                ('content_type', models.PositiveSmallIntegerField(choices=[(0, '培训内容'), (1, '培训总结'), (2, '培训反馈')], verbose_name='内容类型')),
                ('content', models.TextField(verbose_name='内容')),
                ('record', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='training_record.Record', verbose_name='培训记录')),
            ],
            options={
                'verbose_name': '培训记录内容',
                'verbose_name_plural': '培训记录内容',
            },
        ),
        migrations.CreateModel(
            name='StatusChangeLog',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('pre_status', models.PositiveSmallIntegerField(blank=True, choices=[(0, '已提交'), (1, '院系管理员已审核'), (2, '学校管理员已审核')], null=True, verbose_name='更改前状态')),
                ('post_status', models.PositiveSmallIntegerField(blank=True, choices=[(0, '已提交'), (1, '院系管理员已审核'), (2, '学校管理员已审核')], null=True, verbose_name='更改后状态')),
                ('time', models.DateTimeField(verbose_name='更改时间')),
                ('record', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='training_record.Record', verbose_name='培训记录')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to=settings.AUTH_USER_MODEL, verbose_name='操作用户')),
            ],
            options={
                'verbose_name': '培训记录状态更改日志',
                'verbose_name_plural': '培训记录状态更改日志',
            },
        ),
    ]
