# Generated by Django 2.2 on 2019-05-15 12:45

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('training_record', '0004_auto_20190515_1952'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='campuseventfeedback',
            options={'default_permissions': (), 'permissions': (('view_campuseventfeedback', '允许查看培训活动反馈'), ('add_campuseventfeedback', '允许增加培训活动反馈')), 'verbose_name': '培训活动反馈', 'verbose_name_plural': '培训活动反馈'},
        ),
    ]