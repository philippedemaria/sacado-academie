# Generated by Django 3.0.5 on 2022-09-15 07:55

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('lesson', '0003_event_is_validate'),
    ]

    operations = [
        migrations.AlterField(
            model_name='connexioneleve',
            name='event',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='ConnexionEleves', to='lesson.Event'),
        ),
        migrations.AlterField(
            model_name='connexioneleve',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='ConnexionEleves', to=settings.AUTH_USER_MODEL),
        ),
    ]
