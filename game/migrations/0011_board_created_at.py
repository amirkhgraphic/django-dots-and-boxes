# Generated by Django 4.2.13 on 2024-06-29 19:08

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('game', '0010_alter_board_winner'),
    ]

    operations = [
        migrations.AddField(
            model_name='board',
            name='created_at',
            field=models.DateTimeField(auto_created=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
    ]