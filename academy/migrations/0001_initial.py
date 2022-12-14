# Generated by Django 3.0.5 on 2022-03-30 22:11

import academy.models
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('account', '0017_auto_20220328_0857'),
        ('socle', '0006_auto_20211006_2229'),
    ]

    operations = [
        migrations.CreateModel(
            name='Autotest',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('dateback', models.DateTimeField(blank=True, verbose_name='A partir du ?')),
                ('date', models.DateTimeField(auto_now=True)),
                ('file', models.FileField(upload_to=academy.models.directory_path, verbose_name='Fichier pdf')),
                ('is_done', models.BooleanField(default=0, editable=False)),
                ('knowledges', models.ForeignKey(blank=True, editable=False, on_delete=django.db.models.deletion.CASCADE, related_name='autotests', to='socle.Knowledge')),
                ('student', models.ForeignKey(blank=True, editable=False, on_delete=django.db.models.deletion.CASCADE, related_name='autotests', to='account.Student')),
            ],
        ),
    ]
