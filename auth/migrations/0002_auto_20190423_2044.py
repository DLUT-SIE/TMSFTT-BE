# Generated by Django 2.1.5 on 2019-04-23 12:44

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('tmsftt_auth', '0001_initial'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='role',
            unique_together=set(),
        ),
        migrations.RemoveField(
            model_name='role',
            name='department',
        ),
        migrations.RemoveField(
            model_name='role',
            name='group',
        ),
        migrations.RemoveField(
            model_name='user',
            name='roles',
        ),
        migrations.DeleteModel(
            name='Role',
        ),
    ]
