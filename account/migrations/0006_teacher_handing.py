# Generated by Django 3.0.5 on 2021-10-03 05:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0005_student_ebep'),
    ]

    operations = [
        migrations.AddField(
            model_name='teacher',
            name='handing',
            field=models.CharField(blank=True, editable=False, max_length=255, null=True),
        ),
    ]
