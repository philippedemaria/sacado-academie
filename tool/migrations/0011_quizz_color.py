# Generated by Django 3.0.5 on 2021-10-27 06:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tool', '0010_quizz_folders'),
    ]

    operations = [
        migrations.AddField(
            model_name='quizz',
            name='color',
            field=models.CharField(default='#5d4391', max_length=255, verbose_name='Couleur'),
        ),
    ]
