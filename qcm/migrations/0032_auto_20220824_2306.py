# Generated by Django 3.0.5 on 2022-08-24 22:06

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0026_adhesion_year'),
        ('qcm', '0031_auto_20220824_2303'),
    ]

    operations = [
        migrations.AlterField(
            model_name='supportfile',
            name='author',
            field=models.ForeignKey(editable=False, on_delete=django.db.models.deletion.CASCADE, related_name='supportfiles', to='account.Teacher'),
        ),
    ]
