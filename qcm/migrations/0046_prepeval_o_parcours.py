# Generated by Django 3.0.5 on 2023-03-28 17:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('qcm', '0045_slot_content'),
    ]

    operations = [
        migrations.AddField(
            model_name='prepeval',
            name='o_parcours',
            field=models.ManyToManyField(blank=True, editable=False, related_name='o_prepevals', to='qcm.Parcours'),
        ),
    ]
