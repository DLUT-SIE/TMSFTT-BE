# Generated by Django 2.2 on 2019-05-24 02:09

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('training_event', '0002_campusevent_reviewed'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='campusevent',
            options={'default_permissions': (), 'permissions': (('add_campusevent', '允许添加校内培训活动'), ('view_campusevent', '允许查看校内培训活动'), ('change_campusevent', '允许修改校内培训活动'), ('delete_campusevent', '允许删除校内培训活动'), ('review_campusevent', '允许审核校内培训活动')), 'verbose_name': '校内培训活动', 'verbose_name_plural': '校内培训活动'},
        ),
    ]