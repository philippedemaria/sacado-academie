# Generated by Django 3.0.5 on 2021-10-02 15:50

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('qcm', '0015_remove_blacklist_group'),
    ]

    operations = [
        migrations.AlterField(
            model_name='blacklist',
            name='customexercise',
            field=models.ForeignKey(blank=True, editable=False, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='customexercise_individualisation', to='qcm.Customexercise'),
        ),
    ]
