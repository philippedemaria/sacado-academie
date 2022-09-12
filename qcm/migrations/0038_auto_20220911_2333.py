# Generated by Django 3.0.5 on 2022-09-11 22:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('qcm', '0037_auto_20220906_1128'),
    ]

    operations = [
        migrations.AlterField(
            model_name='course',
            name='forme',
            field=models.CharField(blank=True, choices=[('ACTIVITE', 'ACTIVITE'), ('APPLICATION', 'APPLICATION'), ('COURS', 'COURS'), ('CONSIGNE', 'CONSIGNE'), ('EXEMPLE', 'EXEMPLE'), ('EXPLICATION', 'EXPLICATION'), ('HISTOIRE', 'HISTOIRE'), ('ILLUSTRATION', 'ILLUSTRATION'), ('MÉTHODE', 'MÉTHODE'), ('', 'PRESENTATION'), ('VIDEO', 'VIDEO')], default='COURS', max_length=50, verbose_name='Type'),
        ),
    ]
