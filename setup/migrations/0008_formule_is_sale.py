# Generated by Django 3.0.5 on 2022-09-17 11:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('setup', '0007_auto_20220917_1231'),
    ]

    operations = [
        migrations.AddField(
            model_name='formule',
            name='is_sale',
            field=models.BooleanField(default=0, verbose_name='En vente ?'),
        ),
    ]