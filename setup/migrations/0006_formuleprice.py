# Generated by Django 3.0.5 on 2022-08-13 09:38

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('setup', '0005_auto_20220430_1541'),
    ]

    operations = [
        migrations.CreateModel(
            name='Formuleprice',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('price', models.DecimalField(decimal_places=2, max_digits=6, verbose_name='Montant')),
                ('nb_month', models.PositiveIntegerField(default=1, verbose_name='Nombre de mois')),
                ('formule', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='prices', to='setup.Formule', verbose_name='Menu')),
            ],
        ),
    ]
