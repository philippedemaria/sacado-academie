# Generated by Django 3.0.5 on 2022-09-15 10:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('association', '0004_remove_accounting_is_facturation'),
    ]

    operations = [
        migrations.AddField(
            model_name='accounting',
            name='is_facturation',
            field=models.BooleanField(default=0, verbose_name="Affiche la facture sur l'interface client ?"),
        ),
    ]