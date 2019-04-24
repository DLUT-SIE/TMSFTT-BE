# Generated by Django 2.1.5 on 2019-04-24 01:49

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('tmsftt_auth', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Program',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=64, verbose_name='项目名称')),
            ],
            options={
                'verbose_name': '培训项目',
                'verbose_name_plural': '培训项目',
                'permissions': (('add_program', '允许添加培训项目'), ('view_program', '允许查看培训项目'), ('change_program', '允许修改培训项目'), ('delete_program', '允许删除培训项目')),
                'default_permissions': (),
            },
        ),
        migrations.CreateModel(
            name='ProgramCategory',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=64, verbose_name='培训类别名称')),
            ],
            options={
                'verbose_name': '培训类别',
                'verbose_name_plural': '培训类别',
                'permissions': (('add_programcategory', '允许添加通知'), ('view_programcategory', '允许查看通知'), ('change_programcategory', '允许修改通知'), ('delete_programcategory', '允许删除通知')),
                'default_permissions': (),
            },
        ),
        migrations.CreateModel(
            name='ProgramForm',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=64, verbose_name='培训形式名称')),
            ],
            options={
                'verbose_name': '培训形式',
                'verbose_name_plural': '培训形式',
                'permissions': (('add_programform', '允许添加培训形式'), ('view_programform', '允许查看培训形式'), ('change_programform', '允许修改培训形式'), ('delete_programform', '允许删除培训形式')),
                'default_permissions': (),
            },
        ),
        migrations.AddField(
            model_name='program',
            name='category',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='training_program.ProgramCategory', verbose_name='培训类别'),
        ),
        migrations.AddField(
            model_name='program',
            name='department',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='tmsftt_auth.Department', verbose_name='开设单位'),
        ),
        migrations.AddField(
            model_name='program',
            name='form',
            field=models.ManyToManyField(blank=True, to='training_program.ProgramForm', verbose_name='培训形式'),
        ),
    ]
