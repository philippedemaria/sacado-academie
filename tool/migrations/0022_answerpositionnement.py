# Generated by Django 3.0.5 on 2022-10-01 13:42

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('tool', '0021_auto_20221001_0833'),
    ]

    operations = [
        migrations.CreateModel(
            name='Answerpositionnement',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('student', models.CharField(editable=False, max_length=255)),
                ('answer', models.CharField(blank=True, max_length=255, null=True, verbose_name='Réponse')),
                ('score', models.PositiveIntegerField(default=0, editable=False)),
                ('timer', models.CharField(editable=False, max_length=255)),
                ('is_correct', models.BooleanField(default=0, editable=False)),
                ('positionnement', models.ForeignKey(default='', on_delete=django.db.models.deletion.CASCADE, related_name='answerpositionnements', to='tool.Positionnement')),
                ('qrandom', models.ForeignKey(blank=True, editable=False, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='answerpositionnements', to='tool.Generate_qr')),
                ('question', models.ForeignKey(blank=True, editable=False, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='answerpositionnements', to='tool.Question')),
            ],
        ),
    ]