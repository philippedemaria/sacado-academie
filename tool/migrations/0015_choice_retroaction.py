# Generated by Django 3.0.5 on 2022-02-04 15:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tool', '0014_auto_20220204_1522'),
    ]

    operations = [
        migrations.AddField(
            model_name='choice',
            name='retroaction',
            field=models.TextField(blank=True, default='', max_length=255, null=True, verbose_name='Rétroaction'),
        ),
    ]
