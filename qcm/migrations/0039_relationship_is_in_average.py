# Generated by Django 3.0.5 on 2022-10-06 08:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('qcm', '0038_auto_20220911_2333'),
    ]

    operations = [
        migrations.AddField(
            model_name='relationship',
            name='is_in_average',
            field=models.BooleanField(blank=True, default=0, editable=False),
        ),
    ]