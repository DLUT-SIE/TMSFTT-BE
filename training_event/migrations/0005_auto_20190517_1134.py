# Generated by Django 2.2 on 2019-05-17 03:34

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('training_event', '0004_auto_20190515_1952'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='enrollment',
            options={'default_permissions': (), 'permissions': (('add_enrollment', '允许添加活动报名记录'), ('delete_enrollment', '允许删除活动报名记录')), 'verbose_name': '活动报名记录', 'verbose_name_plural': '活动报名记录'},
        ),
    ]