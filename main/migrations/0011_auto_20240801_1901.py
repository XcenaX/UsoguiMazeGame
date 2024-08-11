# Generated by Django 3.2.16 on 2024-08-01 14:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0010_game_ready_players'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='game',
            name='ready_players',
        ),
        migrations.AddField(
            model_name='player',
            name='ready',
            field=models.BooleanField(default=False),
        ),
    ]