# Generated by Django 3.0.5 on 2022-09-22 09:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('lesson', '0010_auto_20220922_1046'),
    ]

    operations = [
        migrations.AlterField(
            model_name='event',
            name='is_private',
            field=models.BooleanField(default=1, verbose_name='Privée ?'),
        ),
    ]