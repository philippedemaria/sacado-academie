# Generated by Django 3.0.5 on 2022-09-17 17:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0027_facture_is_lesson'),
    ]

    operations = [
        migrations.AddField(
            model_name='teacher',
            name='tarif',
            field=models.DecimalField(blank=True, decimal_places=2, default=0, max_digits=10),
        ),
    ]
