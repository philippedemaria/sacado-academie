# Generated by Django 3.0.5 on 2022-09-27 13:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tool', '0019_positionnement'),
    ]

    operations = [
        migrations.AlterField(
            model_name='positionnement',
            name='title',
            field=models.CharField(default='Test de positionnement', max_length=255, verbose_name='Titre du test de positionnement'),
        ),
    ]