# Generated by Django 4.1.13 on 2024-08-02 12:42

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0012_chatmessage'),
    ]

    operations = [
        migrations.AlterField(
            model_name='game',
            name='player_1',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='game_player_1', to='main.player', verbose_name='Игрок 1'),
        ),
    ]