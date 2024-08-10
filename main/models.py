from django.db import models
from django.contrib.auth.models import AbstractUser
import secrets
from parler.models import TranslatableModel, TranslatedFields
from django.utils.translation import gettext_lazy as _
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer


CELL_STATUS = (
    (0, 'Пусто'),
    (1, 'Игрок'),
    (2, 'Вход'),
    (3, 'Выход'),
)

GAME_TYPE = (
    (0, 'Рейтинговая игра'),
    (1, 'Игра на деньги'),
)

RATING_COEFS = {
    "0": {
        "win":{
            "min_rating": 10,
            "initial_rating": 30,
            "max_rating": 60,
            "diff_coefficient": 8
        },
        "lose":{
            "min_rating": -10,
            "initial_rating": -40,
            "max_rating": -70,
            "diff_coefficient": 8
        }
    },
    "1000": {
        "win":{
            "min_rating": 10,
            "initial_rating": 25,
            "max_rating": 60,
            "diff_coefficient": 8
        },
        "lose":{
            "min_rating": -20,
            "initial_rating": -50,
            "max_rating": -80,
            "diff_coefficient": 8
        }
    },
    "2000": {
        "win":{
            "min_rating": 10,
            "initial_rating": 20,
            "max_rating": 50,
            "diff_coefficient": 7
        },
        "lose":{
            "min_rating": -25,
            "initial_rating": -50,
            "max_rating": -80,
            "diff_coefficient": 9
        }
    },
    "3000": {
        "win":{
            "min_rating": 10,
            "initial_rating": 10,
            "max_rating": 40,
            "diff_coefficient": 6
        },
        "lose":{
            "min_rating": -30,
            "initial_rating": -50,
            "max_rating": -100,
            "diff_coefficient": 10
        }
    }
}

class Achievement(TranslatableModel):
    code = models.TextField(default="")    
    icon = models.ImageField(upload_to='achievement_icons/')

    translations = TranslatedFields(
        name = models.CharField(_("Name"), max_length=200),
        description = models.CharField(_("Description"), max_length=400)
    )
    
    def __str__(self):
        return self.name

class Rank(TranslatableModel):
    rating = models.IntegerField()
    icon = models.ImageField(upload_to='ranks_icons/')
    
    translations = TranslatedFields(
        name = models.CharField(_("Name"), max_length=200)     
    )

    def __str__(self):
        return self.name


class User(AbstractUser):
    rating = models.IntegerField(default=500, verbose_name='Рейтинг')
    rank = models.ForeignKey(Rank, on_delete=models.DO_NOTHING, related_name='users', verbose_name='Ранг', blank=True, null=True)
    balance = models.IntegerField(default=1000, verbose_name='Баланс')
    achievements = models.ManyToManyField(Achievement, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    wins = models.IntegerField(default=0, verbose_name='Победы')
    loses = models.IntegerField(default=0, verbose_name='Поражения')

    def set_rating(self, new_rating):
        self.rating = max(0, new_rating)
        if(self.rating == 0):
            try:
                achivement = self.achievements.get(code="useless_shit")
                self.achievements.add(achivement)
            except:
                pass
        elif(self.rating > 1000):
            pass

        self.save()

    
    def get_win_gain(self, opponent_rating):
        """Возвращает то, сколько рейтинга ты получишь в случае победы. Если соперник слишком слаб то 0"""
        for key, value in RATING_COEFS.items():
            if self.rating >= int(key):
                min_rating = value["win"]["min_rating"]
                initial_rating = value["win"]["initial_rating"]
                max_rating = value["win"]["max_rating"]
                diff_coefficient = value["win"]["diff_coefficient"]
                break
        diff = opponent_rating - self.rating 
        return max(min_rating, min(max_rating, (initial_rating + (diff // diff_coefficient))))
    
    def get_lose_gain(self, opponent_rating):
        """Возвращает то, сколько рейтинга ты потеряешь в случае поражения. Если соперник слишком силен ты все равно теряешь рейтинг"""        
        for key, value in RATING_COEFS.items():
            if self.rating >= int(key):
                min_rating = value["lose"]["min_rating"]
                initial_rating = value["lose"]["initial_rating"]
                max_rating = value["lose"]["max_rating"]
                diff_coefficient = value["lose"]["diff_coefficient"]
                break
        diff = self.rating - opponent_rating
        return min(min_rating, max(max_rating, (initial_rating - (diff // diff_coefficient))))


    def get_rank(self):
        ranks = Rank.objects.filter(rating__lte=self.rating).order_by('-rating')
        if ranks.exists():
            return ranks.first().name
        return ""

    def check_new_achivements(self):
        pass

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return self.username


def empty_board():
    return {
        "player_position": None,
        "entrance_position": None,
        "exit_position": None,
        "walls": [],
        "spotted_walls": [] # стены которые игрок обнаружил у противника
    }

class Player(models.Model):
    session_key = models.CharField(max_length=40, blank=True, null=True) # для анонимных пользователей
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Пользователь', blank=True, null=True)
    board = models.JSONField("Board", default=empty_board)
    current_turn = models.BooleanField(default=False)
    ready = models.BooleanField(default=False)

    class Meta:
        verbose_name = 'Игрок'
        verbose_name_plural = 'Игроки'

    def __str__(self):
        return str(self.user) if self.user else "Anonymous"

class Game(models.Model):
    code = models.CharField(max_length=10, unique=True, verbose_name='Код комнаты', blank=True)
    name = models.TextField(blank=True, null=True, verbose_name="Имя")
    player_1 = models.ForeignKey(Player, on_delete=models.CASCADE, related_name='game_player_1', verbose_name='Игрок 1', blank=True, null=True)
    player_2 = models.ForeignKey(Player, on_delete=models.CASCADE, related_name='game_player_2', verbose_name='Игрок 2', blank=True, null=True)
    is_active = models.BooleanField(default=True, verbose_name='Активна')
    is_private = models.BooleanField(default=False, verbose_name='Приватная')
    password = models.TextField(blank=True, null=True, verbose_name="Пароль")
    game_type = models.PositiveSmallIntegerField(choices=GAME_TYPE, default=0, verbose_name='Тип игры')
    bet = models.IntegerField(verbose_name='Ставка', blank=True, null=True)
    game_stage = models.IntegerField(default=1, verbose_name='Стадия игры')
    winner = models.TextField(default="", verbose_name="ник победителя", blank=True, null=True)
    
    def ready_players(self):
        count = 0
        if self.player_1 and self.player_1.ready:
            count += 1
        if self.player_2 and self.player_2.ready:
            count += 1
        return count
    
    def players(self):
        count = 0
        if self.player_1:
            count += 1
        if self.player_2:
            count += 1
        return count
    
    def has_user(self, user):
        return (
            (self.player_1 and (self.player_1.user == user or self.player_1.session_key == user)) or 
            (self.player_2 and (self.player_2.user == user or self.player_2.session_key == user))
        )
    
    def get_me_opponent(self, current_user):
        if current_user == self.player_1.user or current_user == self.player_1.session_key:
            me = self.player_1
            opponent = self.player_2
        else:
            me = self.player_2
            opponent = self.player_1
        return me, opponent
    
    def get_current_turn_player(self):
        return self.player_1 if self.player_1.current_turn else self.player_2
    
    def notify_game_update(self, action):
        channel_layer = get_channel_layer()
        message = {
            "action": action,
            "game": {
                "id": self.id,
                "name": self.name,
                "is_private": self.is_private,
                "code": self.code,
            },
        }
        async_to_sync(channel_layer.group_send)(
            "games",
            {
                "type": "send_game_update",
                "message": message,
            }
        )
    
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

class ChatMessage(models.Model):
    game = models.ForeignKey(Game, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True)
    session_key = models.CharField(max_length=40, blank=True, null=True) # для анонимных пользователей
    text = models.TextField(max_length=200)
    created_at = models.DateTimeField(auto_now=True) # Как сделать чтобы у каждого человека отображалось его локальное время?
    
    def __str__(self):
        username = self.user.username if self.user else "Anonymous"
        return f"Игра {self.game.code}. {self.created_at} ({username}): {self.text}"