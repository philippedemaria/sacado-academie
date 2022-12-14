# Generated by Django 3.0.5 on 2021-11-05 09:25

import ckeditor_uploader.fields
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('bibliotex', '0010_exotex_content_html'),
    ]

    operations = [
        migrations.AddField(
            model_name='exotex',
            name='correction_html',
            field=ckeditor_uploader.fields.RichTextUploadingField(blank=True, verbose_name='Correction pour html'),
        ),
        migrations.AlterField(
            model_name='exotex',
            name='content_html',
            field=ckeditor_uploader.fields.RichTextUploadingField(blank=True, verbose_name='Enoncé pour html'),
        ),
    ]
