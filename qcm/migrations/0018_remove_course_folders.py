# Generated by Django 3.0.5 on 2021-10-23 07:58

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('qcm', '0017_auto_20211022_2103'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='course',
            name='folders',
        ),
    ]
