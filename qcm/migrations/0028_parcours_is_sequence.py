# Generated by Django 3.0.5 on 2022-07-09 15:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('qcm', '0027_exercise_audiofile'),
    ]

    operations = [
        migrations.AddField(
            model_name='parcours',
            name='is_sequence',
            field=models.BooleanField(default=0, verbose_name="Séquence d'apprentissage ?"),
        ),
    ]
