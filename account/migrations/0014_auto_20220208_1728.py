# Generated by Django 3.0.5 on 2022-02-08 16:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0013_auto_20220208_1522'),
    ]

    operations = [
        migrations.AlterField(
            model_name='avatar',
            name='level',
            field=models.PositiveSmallIntegerField(choices=[(50, 'moins de 50%'), (70, 'moins de 70%'), (85, 'moins de 85%')]),
        ),
    ]
