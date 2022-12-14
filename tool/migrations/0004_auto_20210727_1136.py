# Generated by Django 3.0.5 on 2021-07-27 10:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('group', '0001_initial'),
        ('tool', '0003_quizz_is_archive'),
    ]



    operations = [
        migrations.AddField(
            model_name='diaporama',
            name='is_archive',
            field=models.BooleanField(default=0, verbose_name='Archivé ?'),
        ),
        migrations.AlterField(
            model_name='diaporama',
            name='groups',
            field=models.ManyToManyField(blank=True, related_name='presentation', to='group.Group'),
        ),
    ]
