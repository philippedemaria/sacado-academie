# Generated by Django 3.0.5 on 2022-05-05 16:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0021_facture_date'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='adhesion',
            name='menu',
        ),
        migrations.AddField(
            model_name='adhesion',
            name='formule_id',
            field=models.PositiveIntegerField(blank=True, editable=False, null=True, verbose_name='Formule'),
        ),
    ]
