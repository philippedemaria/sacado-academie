# Generated by Django 3.0.5 on 2021-10-23 17:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('qcm', '0018_remove_course_folders'),
    ]

    operations = [
        migrations.AddField(
            model_name='parcours',
            name='is_active',
            field=models.BooleanField(default=0, verbose_name="Page d'accueil élève"),
        ),
    ]
