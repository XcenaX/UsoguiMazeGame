from django.shortcuts import render, redirect
from django.views.generic import ListView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseBadRequest
from .models import Game
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views.generic import DetailView


class HomePage(LoginRequiredMixin, ListView):
    model = Game
    template_name = 'home.html'
    context_object_name = 'games'
    paginate_by = 20
    login_url = '/accounts/login/'

    def get_queryset(self):
        return Game.objects.filter(is_active=True).order_by('-id')

    def post(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return HttpResponseBadRequest("Необходима авторизация")
        
        new_game = Game.objects.create(player_1=request.user.player, is_active=True)
        
        return redirect('some_view_to_display_game', game_id=new_game.id)


class GameView(DetailView):
    model = Game
    template_name = 'game_detail.html'  # Указывает имя шаблона, который будет использоваться
    context_object_name = 'game'  # Имя объекта, через которое он будет доступен в шаблоне
    slug_field = 'code'  # Указывает, какое поле модели используется как slug
    slug_url_kwarg = 'code'  # Имя аргумента slug в URLconf