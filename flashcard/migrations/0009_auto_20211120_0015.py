# Generated by Django 3.0.5 on 2021-11-19 23:15

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('flashcard', '0008_remove_flashcard_duration'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='flashcard',
            name='size',
        ),
        migrations.RemoveField(
            model_name='flashcard',
            name='sizea',
        ),
        migrations.RemoveField(
            model_name='flashcard',
            name='sizeh',
        ),
    ]
