# Generated by Django 3.0.5 on 2022-01-30 19:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('socle', '0006_auto_20211006_2229'),
        ('flashcard', '0024_auto_20220127_1055'),
    ]

    operations = [
        migrations.AlterField(
            model_name='flashpack',
            name='themes',
            field=models.ManyToManyField(blank=True, related_name='flashpacks', to='socle.Theme'),
        ),
    ]
