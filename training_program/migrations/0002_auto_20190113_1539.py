# Generated by Django 2.1.5 on 2019-01-13 07:39

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('training_program', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='program',
            old_name='category',
            new_name='catgegory',
        ),
    ]