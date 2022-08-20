# Generated by Django 3.0.5 on 2022-08-20 13:41

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0026_adhesion_year'),
        ('group', '0004_auto_20210919_1915'),
    ]

    operations = [
        migrations.AlterField(
            model_name='sharing_group',
            name='group',
            field=models.ForeignKey(blank=True, editable=False, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='group_sharingteacher', to='group.Group'),
        ),
        migrations.AlterField(
            model_name='sharing_group',
            name='teacher',
            field=models.ForeignKey(blank=True, editable=False, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='teacher_sharingteacher', to='account.Teacher'),
        ),
    ]
