# Generated by Django 2.2 on 2019-05-15 12:45

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('tmsftt_auth', '0007_user_cell_phone_number'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='department',
            options={'default_permissions': (), 'verbose_name': '院系', 'verbose_name_plural': '院系'},
        ),
        migrations.AlterModelOptions(
            name='user',
            options={'default_permissions': (), 'verbose_name': '用户', 'verbose_name_plural': '用户'},
        ),
    ]