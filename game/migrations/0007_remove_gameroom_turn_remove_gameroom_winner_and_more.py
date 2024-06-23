# Generated by Django 4.2.13 on 2024-06-22 14:45

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('game', '0006_gameroom_online_users'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='gameroom',
            name='turn',
        ),
        migrations.RemoveField(
            model_name='gameroom',
            name='winner',
        ),
        migrations.AddField(
            model_name='board',
            name='guest',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='guest_games', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='board',
            name='host',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='host_games', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='board',
            name='turn',
            field=models.CharField(choices=[('host', 'Host'), ('guest', 'Guest')], default='host', max_length=7),
        ),
        migrations.AddField(
            model_name='board',
            name='winner',
            field=models.CharField(blank=True, choices=[('host', 'Host'), ('guest', 'Guest')], max_length=7, null=True),
        ),
    ]
