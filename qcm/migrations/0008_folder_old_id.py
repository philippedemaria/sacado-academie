# Generated by Django 3.0.5 on 2021-09-19 18:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('qcm', '0007_auto_20210919_1949'),
    ]

    operations = [
        migrations.AddField(
            model_name='folder',
            name='old_id',
            field=models.PositiveIntegerField(blank=True, default=0, editable=False, null=True),
        ),
    ]
