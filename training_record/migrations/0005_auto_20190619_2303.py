# Generated by Django 2.2 on 2019-06-19 15:03

from django.conf import settings
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('training_event', '0006_auto_20190613_1439'),
        ('training_record', '0004_auto_20190612_2142'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='record',
            unique_together={('user', 'campus_event')},
        ),
    ]
