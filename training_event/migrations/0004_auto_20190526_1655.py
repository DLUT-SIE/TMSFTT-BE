# Generated by Django 2.2 on 2019-05-26 08:55

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('training_event', '0003_auto_20190524_1009'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='eventcoefficient',
            unique_together={('campus_event', 'role'), ('off_campus_event', 'role')},
        ),
    ]