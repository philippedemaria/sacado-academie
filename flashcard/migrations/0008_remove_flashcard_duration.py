# Generated by Django 3.0.5 on 2021-11-18 06:42

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('flashcard', '0007_flashcard_sizeh'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='flashcard',
            name='duration',
        ),
    ]
