# Generated by Django 3.0.5 on 2022-09-18 19:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('socle', '0007_subject_is_active'),
        ('tool', '0017_auto_20220402_0014'),
    ]

    operations = [
        migrations.AddField(
            model_name='tool',
            name='levels',
            field=models.ManyToManyField(blank=True, related_name='tools', to='socle.Level'),
        ),
    ]
