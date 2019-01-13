# Generated by Django 2.1.5 on 2019-01-13 06:41

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('training_record', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='ReviewNote',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('create_time', models.DateTimeField(auto_now_add=True, verbose_name='创建时间')),
                ('field_name', models.CharField(max_length=32, verbose_name='字段名称')),
                ('content', models.CharField(max_length=128, verbose_name='提示内容')),
                ('record', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='training_record.Record', verbose_name='培训记录')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='创建用户')),
            ],
            options={
                'verbose_name': '培训记录审核提示',
                'verbose_name_plural': '培训记录审核提示',
            },
        ),
    ]
