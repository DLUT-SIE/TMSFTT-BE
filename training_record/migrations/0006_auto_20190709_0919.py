# Generated by Django 2.2 on 2019-07-09 01:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('training_record', '0005_auto_20190619_2303'),
    ]

    operations = [
        migrations.AlterField(
            model_name='campuseventfeedback',
            name='content',
            field=models.CharField(max_length=500, verbose_name='反馈内容'),
        ),
    ]
