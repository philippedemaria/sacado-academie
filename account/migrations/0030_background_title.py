# Generated by Django 3.0.5 on 2022-10-14 14:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0029_user_backtitle'),
    ]

    operations = [
        migrations.AddField(
            model_name='background',
            name='title',
            field=models.BooleanField(default=0),
        ),
    ]
