# Generated by Django 3.0.5 on 2021-08-18 04:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0002_newpassword'),
    ]

    operations = [
        migrations.AlterField(
            model_name='newpassword',
            name='email',
            field=models.CharField(max_length=255),
        ),
    ]
