# Generated by Django 3.0.5 on 2022-04-30 14:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('setup', '0004_tweeter'),
    ]

    operations = [
        migrations.AlterField(
            model_name='formule',
            name='price',
            field=models.DecimalField(decimal_places=2, max_digits=6, verbose_name='Montant'),
        ),
    ]
