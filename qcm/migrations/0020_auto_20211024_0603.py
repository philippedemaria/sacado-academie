# Generated by Django 3.0.5 on 2021-10-24 05:03

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('qcm', '0019_parcours_is_active'),
    ]

    operations = [
        migrations.AlterField(
            model_name='course',
            name='parcours',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='course', to='qcm.Parcours'),
        ),
    ]
