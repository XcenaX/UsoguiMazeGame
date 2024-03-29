from django.db import models
from django.contrib.auth.models import User
import secrets

class Cell(models.Model):
    x_coordinate = models.IntegerField(verbose_name='Координата X')
    y_coordinate = models.IntegerField(verbose_name='Координата Y')
    is_entry = models.BooleanField(default=False, verbose_name='Вход')
    is_exit = models.BooleanField(default=False, verbose_name='Выход')

    class Meta:
        verbose_name = 'Клетка'
        verbose_name_plural = 'Клетки'

    def __str__(self):
        return f"Клетка ({self.x_coordinate}, {self.y_coordinate})"

class Wall(models.Model):
    cell_1 = models.ForeignKey(Cell, on_delete=models.CASCADE, related_name='wall_cell_1', verbose_name='Клетка 1')
    cell_2 = models.ForeignKey(Cell, on_delete=models.CASCADE, related_name='wall_cell_2', verbose_name='Клетка 2')
    
    class Meta:
        verbose_name = 'Стена'
        verbose_name_plural = 'Стены'

    def __str__(self):
        return f"Стена между {self.cell_1} и {self.cell_2} ({'Вертикальная' if self.orientation == 'V' else 'Горизонтальная'})"

class Player(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Пользователь')
    current_cell = models.ForeignKey(Cell, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='Текущая клетка')

    class Meta:
        verbose_name = 'Игрок'
        verbose_name_plural = 'Игроки'

    def __str__(self):
        return self.user.username

class Game(models.Model):
    code = models.CharField(max_length=10, unique=True, verbose_name='Код комнаты')
    player_1 = models.ForeignKey(Player, on_delete=models.CASCADE, related_name='game_player_1', verbose_name='Игрок 1')
    player_2 = models.ForeignKey(Player, on_delete=models.CASCADE, related_name='game_player_2', verbose_name='Игрок 2')
    current_turn_player = models.ForeignKey(Player, on_delete=models.CASCADE, related_name='current_turn', verbose_name='Текущий ход игрока')
    is_active = models.BooleanField(default=True, verbose_name='Активна')
    is_private = models.BooleanField(default=False, verbose_name='Приватная')

    class Meta:
        verbose_name = 'Игра'
        verbose_name_plural = 'Игры'

    def save(self, *args, **kwargs):
        if not self.code:
            self.code = self.generate_unique_code()
        super().save(*args, **kwargs)

    def generate_unique_code(self):
        while True:
            code = secrets.token_urlsafe(5)
            if not Game.objects.filter(code=code).exists():
                return code

    def __str__(self):
        return f"Игра между {self.player_1} и {self.player_2}"
