# Generated by Django 3.0.5 on 2022-08-22 21:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('socle', '0006_auto_20211006_2229'),
    ]

    operations = [
        migrations.AddField(
            model_name='subject',
            name='is_active',
            field=models.BooleanField(default=0, verbose_name='Active ?'),
        ),
    ]
