# Generated by Django 3.0.5 on 2021-11-18 18:22

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0010_remove_user_gar_token'),
        ('tool', '0011_quizz_color'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='answerplayer',
            name='gquizz',
        ),
        migrations.RemoveField(
            model_name='display_question',
            name='gquizz',
        ),
        migrations.RemoveField(
            model_name='generate_qr',
            name='gquizz',
        ),
        migrations.AddField(
            model_name='answerplayer',
            name='quizz',
            field=models.ForeignKey(default='', on_delete=django.db.models.deletion.CASCADE, related_name='answerplayer', to='tool.Quizz'),
        ),
        migrations.AddField(
            model_name='display_question',
            name='quizz',
            field=models.ForeignKey(default='', editable=False, on_delete=django.db.models.deletion.CASCADE, related_name='display_questions', to='tool.Quizz'),
        ),
        migrations.AddField(
            model_name='generate_qr',
            name='quizz',
            field=models.ForeignKey(default='', editable=False, on_delete=django.db.models.deletion.CASCADE, related_name='generate_qr', to='tool.Quizz'),
        ),
        migrations.AddField(
            model_name='quizz',
            name='students',
            field=models.ManyToManyField(blank=True, editable=False, related_name='quizz', to='account.Student'),
        ),
        migrations.DeleteModel(
            name='Generate_quizz',
        ),
    ]
