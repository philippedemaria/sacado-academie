# Generated by Django 3.0.5 on 2022-11-28 10:45

import ckeditor_uploader.fields
from django.db import migrations, models
import django.db.models.deletion
import qcm.models


class Migration(migrations.Migration):

    dependencies = [
        ('qcm', '0039_relationship_is_in_average'),
    ]

    operations = [
        migrations.CreateModel(
            name='Choice',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('imageanswer', models.ImageField(blank=True, default='', null=True, upload_to=qcm.models.choice_directory_path, verbose_name='Image')),
                ('answer', models.TextField(blank=True, default='', max_length=255, null=True, verbose_name='Réponse écrite')),
                ('retroaction', models.TextField(blank=True, default='', max_length=255, null=True, verbose_name='Rétroaction')),
                ('imageanswerbis', models.ImageField(blank=True, default='', null=True, upload_to=qcm.models.choice_directory_path, verbose_name='Image par paire')),
                ('answerbis', models.TextField(blank=True, default='', max_length=255, null=True, verbose_name='Réponse par paire')),
                ('is_correct', models.BooleanField(default=0, verbose_name='Réponse correcte ?')),
            ],
        ),
        migrations.CreateModel(
            name='Etype',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.TextField(blank=True, default='', max_length=255, verbose_name='Type')),
                ('imagefile', models.ImageField(blank=True, default='', upload_to=qcm.models.etype_directory_path, verbose_name='Image')),
                ('html', models.TextField(blank=True, default='', verbose_name='Html éventuel')),
                ('url', models.CharField(blank=True, default='', max_length=255, verbose_name='url')),
                ('is_online', models.BooleanField(default=0, verbose_name='En ligne ?')),
                ('template', models.CharField(blank=True, default='', max_length=255, verbose_name='template')),
                ('ranking', models.PositiveIntegerField(default=0)),
            ],
        ),
        migrations.AddField(
            model_name='customexercise',
            name='filltheblanks',
            field=ckeditor_uploader.fields.RichTextUploadingField(blank=True, default='', verbose_name='Texte à trous'),
        ),
        migrations.AddField(
            model_name='customexercise',
            name='precision',
            field=models.FloatField(blank=True, null=True, verbose_name='Précision'),
        ),
        migrations.AddField(
            model_name='customexercise',
            name='pseudoalea_nb',
            field=models.PositiveIntegerField(blank=True, default=0),
        ),
        migrations.AddField(
            model_name='customexercise',
            name='tick',
            field=models.FloatField(blank=True, null=True, verbose_name='Graduation'),
        ),
        migrations.AddField(
            model_name='customexercise',
            name='xmax',
            field=models.FloatField(blank=True, null=True, verbose_name='x max '),
        ),
        migrations.AddField(
            model_name='customexercise',
            name='xmin',
            field=models.FloatField(blank=True, null=True, verbose_name='x min '),
        ),
        migrations.CreateModel(
            name='Variable',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(blank=True, max_length=50, verbose_name='variable')),
                ('is_integer', models.BooleanField(default=1, verbose_name='Valeur entière ?')),
                ('maximum', models.IntegerField(default=10)),
                ('minimum', models.IntegerField(default=0)),
                ('words', models.CharField(blank=True, max_length=255, verbose_name='Liste de valeurs')),
                ('customexercise', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='variables', to='qcm.Customexercise')),
            ],
        ),
        migrations.CreateModel(
            name='Subchoice',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('imageanswer', models.ImageField(blank=True, default='', null=True, upload_to=qcm.models.choice_directory_path, verbose_name='Image')),
                ('answer', models.TextField(blank=True, default='', max_length=255, null=True, verbose_name='Réponse écrite')),
                ('retroaction', models.TextField(blank=True, default='', max_length=255, null=True, verbose_name='Rétroaction')),
                ('is_correct', models.BooleanField(default=0, verbose_name='Réponse correcte ?')),
                ('choice', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='subchoices', to='qcm.Choice')),
            ],
        ),
        migrations.AddField(
            model_name='choice',
            name='customexercise',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='choices', to='qcm.Customexercise'),
        ),
    ]
