# Generated by Django 2.2 on 2019-05-26 04:22

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('tmsftt_auth', '0001_initial'),
    ]

    operations = [
        migrations.DeleteModel(
            name='UserPermission',
        ),
    ]
