# Generated by Django 4.1.13 on 2024-08-02 13:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0014_game_can_spectate'),
    ]

    operations = [
        migrations.AddField(
            model_name='game',
            name='password',
            field=models.TextField(blank=True, null=True, verbose_name='Пароль'),
        ),
    ]