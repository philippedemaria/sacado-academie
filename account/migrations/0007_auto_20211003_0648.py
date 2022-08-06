# Generated by Django 3.0.5 on 2021-10-03 05:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0006_teacher_handing'),
    ]

    operations = [
        migrations.RenameField(
            model_name='teacher',
            old_name='handing',
            new_name='helping',
        ),
        migrations.AddField(
            model_name='teacher',
            name='helping_right',
            field=models.BooleanField(default=0, verbose_name='Aide à distance ?'),
        ),
    ]
