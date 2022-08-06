# Generated by Django 3.0.5 on 2021-09-14 19:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('association', '0011_auto_20210907_1916'),
    ]

    operations = [
        migrations.AlterField(
            model_name='accounting',
            name='mode',
            field=models.CharField(blank=True, choices=[('Période de test', 'Période de test'), ('par carte de crédit', 'Carte de crédit'), ('par virement bancaire', 'Virement bancaire'), ('en espèces', 'Espèces'), ('par mandatement administratif', 'Mandatement administratif')], default='', max_length=255, verbose_name='Mode de paiement'),
        ),
    ]
