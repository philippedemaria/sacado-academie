# Generated by Django 3.0.5 on 2021-07-29 13:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tool', '0005_auto_20210727_1526'),
    ]
    

    operations = [
        migrations.AlterField(
            model_name='diaporama',
            name='is_archive',
            field=models.BooleanField(default=0, verbose_name='Archivé ?'),
        ),
    ]
