# Generated by Django 3.0.5 on 2022-09-15 10:25

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('association', '0005_accounting_is_facturation'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='accounting',
            name='is_facturation',
        ),
    ]
