# Generated by Django 4.1.13 on 2024-08-06 12:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0017_game_winner'),
    ]

    operations = [
        migrations.AlterField(
            model_name='game',
            name='winner',
            field=models.TextField(blank=True, default='', null=True, verbose_name='ник победителя'),
        ),
    ]
