# Generated by Django 3.0.5 on 2021-09-19 22:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('qcm', '0010_folder_is_archive'),
    ]

    operations = [
        migrations.AlterField(
            model_name='folder',
            name='is_archive',
            field=models.BooleanField(default=0, verbose_name='Archive ?'),
        ),
    ]
