# Generated by Django 3.0.5 on 2021-12-03 16:22

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0012_remove_teacher_is_contact'),
        ('flashcard', '0017_auto_20211203_0600'),
    ]

    operations = [
        migrations.CreateModel(
            name='commentflashcard',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('comment', models.CharField(max_length=255, verbose_name='Commentaire')),
                ('date', models.DateField(auto_now=True)),
                ('flashcard', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='comments', to='flashcard.Flashcard')),
                ('teacher', models.ForeignKey(blank=True, editable=False, on_delete=django.db.models.deletion.CASCADE, related_name='comments', to='account.Teacher')),
            ],
        ),
    ]
