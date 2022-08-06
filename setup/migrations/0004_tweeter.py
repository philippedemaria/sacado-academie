# Generated by Django 3.0.5 on 2022-02-25 17:36

import ckeditor_uploader.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('setup', '0003_webinaire'),
    ]

    operations = [
        migrations.CreateModel(
            name='Tweeter',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(blank=True, max_length=255, verbose_name='Titre')),
                ('texte', ckeditor_uploader.fields.RichTextUploadingField(verbose_name='Texte')),
                ('date_created', models.DateTimeField(auto_now_add=True)),
            ],
        ),
    ]
