# Generated by Django 2.2 on 2019-06-20 08:20

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('tmsftt_auth', '0008_departmentadmininformation'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='departmentadmininformation',
            name='dwmc',
        ),
        migrations.RemoveField(
            model_name='departmentadmininformation',
            name='jsxm',
        ),
    ]