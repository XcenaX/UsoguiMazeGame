# Generated by Django 4.2.1 on 2024-04-04 02:02

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0005_remove_game_current_turn_player_player_current_turn_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='game',
            name='player_2',
            field=models.ForeignKey(blank=True, on_delete=django.db.models.deletion.CASCADE, related_name='game_player_2', to='main.player', verbose_name='Игрок 2'),
        ),
    ]
