# Generated by Django 3.0.5 on 2021-12-12 21:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tool', '0012_auto_20211118_1922'),
    ]

    operations = [
        migrations.AlterField(
            model_name='question',
            name='theme',
            field=models.BooleanField(default=1, verbose_name='Thème ?'),
        ),
    ]
