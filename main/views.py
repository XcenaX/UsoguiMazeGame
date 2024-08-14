from urllib import response
from django.shortcuts import render, redirect
from django.views.generic import DetailView
from django.views import View
from django.core.paginator import Paginator

from main.modules.functions import *
from django.contrib.auth.hashers import make_password, check_password
from django.urls import reverse

from django.contrib.auth import authenticate, login, logout

import json

from django.shortcuts import get_object_or_404
from django.http import JsonResponse, HttpResponse
from django.contrib.auth.mixins import LoginRequiredMixin
from main.models import Game, PaymentData, Player, ChatMessage, User
from main.forms import BoardForm

from maze.settings import ERRORS_TYPES, MAX_MESSAGES_IN_CHAT

from django.utils.timezone import localtime

from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

import threading

from django.db.models import Count, Q, F

class LoginView(View):
    template_name = "login.html"

    # def get(self, request, *args, **kwargs):
    #     return render(request, self.template_name)

    def post(self, request, *args, **kwargs):
        data = json.loads(request.body)        
        username = data.get("nickname")
        password = data.get("accountPassword")

        if username == "" or password == "":
            return JsonResponse({"success": False, "error": "Invalid nickname or password"}, status=400)

        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return JsonResponse({"success": True})
        else:
            return JsonResponse({"success": False, "error": "Invalid nickname or password"}, status=400)

        

class RegisterView(View):
    template_name = "register.html"

    # def get(self, request, *args, **kwargs):
    #     return render(request, self.template_name)

    def post(self, request, *args, **kwargs):
        data = json.loads(request.body)        
        username = data.get("nickname")
        password = data.get("accountPassword")

        if username == "" or password == "":
            return JsonResponse({"success": False, "error": "Invalid nickname or password"}, status=400)

        if User.objects.filter(username=username).exists():
            return JsonResponse({"success": False, "error": "Nickname already taken"}, status=400)

        user = User.objects.create(username=username, password=make_password(password))
        login(request, user)
        return JsonResponse({"success": True})
          

class LogoutView(View):
    def post(self, request, *args, **kwargs):
        logout(request)
        return redirect(reverse("home"))

# {% provider_login_url 'google'%}?next=/

class HomePage(View):
    paginate_by = 20

    def get(self, request, *args, **kwargs):
        current_user, authorized = get_current_user(request)
        
        current_game = get_current_game(current_user, authorized)
        games_list = get_available_games(current_user, authorized)
        
        paginator = Paginator(games_list, self.paginate_by)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)

        error_type = request.GET.get('error_type', "")
        error_msg = ""
        if error_type in ERRORS_TYPES:
            error_msg = ERRORS_TYPES[error_type]
        
        context = {
            'page_obj': page_obj,
            'error_type': error_type,
            'error_msg': error_msg,
            'current_game': current_game,
            'current_user': current_user if authorized else "Anonymous"
        }
        return render(request, 'home.html', context)

class QuickJoin(View):
    def post(self, request, *args, **kwargs):
        current_user, authorized= get_current_user(request)

        join_game = get_available_games(current_user, authorized).first()

        player = None
        if authorized:
            player = Player.objects.create(user=current_user, current_turn=True)
        else:
            player = Player.objects.create(session_key=current_user, current_turn=True)

        if not join_game:
            username = "Anonymous" if not authorized else current_user.username
            join_game = Game.objects.create(
                player_1=player,
                name=f"{username}'s game",
                is_private=False                
            )

            join_game.notify_game_update('create')
        else:
            if not join_game.player_1:
                join_game.player_1 = player
            elif not join_game.player_2:
                join_game.player_2 = player
            join_game.save()
            join_game.notify_game_update('delete')

        return redirect(reverse("game", args=[join_game.code]))
        

class CreateGame(View):
    def post(self, request, *args, **kwargs):
        current_user, authorized = get_current_user(request)
        current_game = None

        if authorized:            
            current_game = Game.objects.filter(
                Q(player_1__user=current_user) | Q(player_2__user=current_user)
            ).first()
        else:            
            current_game = Game.objects.filter(
                Q(player_1__session_key=current_user) | Q(player_2__session_key=current_user)
            ).first()        

        if current_game:
            return JsonResponse({'success': False, 'error': 'You already playing in other game room.\nLeave or finish to create new game'})

        data = json.loads(request.body)
        game_name = data.get('gameName')
        is_private = data.get('isPrivate')
        game_password = data.get('gamePassword') if is_private else None

        player = None
        if authorized:
            player = Player.objects.create(user=current_user, current_turn=True)
        else:
            player = Player.objects.create(session_key=current_user, current_turn=True)

        game = Game.objects.create(
            player_1=player,
            name=game_name,
            is_private=is_private,
            password=game_password
        )

        game.notify_game_update('create')

        return JsonResponse({'success': True, 'redirect': reverse("game", args=[game.code])})

class GameView(View):
    model = Game
    context_object_name = 'game'  # Имя объекта, через которое он будет доступен в шаблоне
    slug_field = 'code'  # Указывает, какое поле модели используется как slug
    slug_url_kwarg = 'code'  # Имя аргумента slug в URLconf

    def get(self, request, code, *args, **kwargs):
        try:
            game = Game.objects.get(code=code)
        except:
            return redirect(reverse("home") + "?error_type=game_not_found")
        
        current_user, authorized = get_current_user(request)

        allowed_to_play = game.has_user(current_user)
        if not allowed_to_play:
            return redirect(reverse("home") + "?error_type=not_allowed")

        me, opponent = game.get_me_opponent(current_user)
    
        current_turn_player = game.get_current_turn_player()

        chat_messages = ChatMessage.objects.filter(game=game).order_by('created_at')

        # Группировка сообщений
        grouped_messages = []
        current_group = []
        last_time = None
        last_user = None

        for message in chat_messages:
            local_time = localtime(message.created_at)
            if last_time and ((local_time - last_time).total_seconds() > 60 or (last_user != message.user and last_user != message.session_key)):
                if current_group:
                    grouped_messages.append(current_group)
                current_group = []
            current_group.append(message)
            last_time = local_time
            last_user = message.session_key if message.session_key else message.user
        
        if current_group:
            grouped_messages.append(current_group)

        template_name = 'prepare_game.html'
        can_go = []
        if game.game_stage == 2:
            template_name = 'game.html'
            if me.current_turn:
                can_go = get_available_moves(current_turn_player.board["player_position"], current_turn_player.board["spotted_walls"])

        context = {     
            "session_key": current_user if not authorized else None,
            "my_board": me.board,
            "grouped_messages": grouped_messages,
            "me": me,
            'opponent': opponent,
            "game": game,            
            "can_go": can_go
        }
        return render(request, template_name, context)


class UpdateGameStageView(View):
    def post(self, request, game_id):
        game = get_object_or_404(Game, id=game_id)
        current_user, authorized = get_current_user(request)
        
        me, opponent = game.get_me_opponent(current_user)
            
        if not game.has_user(current_user):
            return JsonResponse({'error': 'You are not allowed to change this board. Btw can you please stop trying to hack this site :)'}, status=403)            
        
        if me.ready:
            return JsonResponse({'error': 'You cant change your board after you are ready'}, status=400)

        try:
            data = json.loads(request.body)
            entrance = data.get('entrance')
            exit = data.get('exit')
            walls = data.get('walls')
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON data'}, status=400)

        form_data = {
            'entrance': json.dumps(entrance),
            'exit': json.dumps(exit),
            'walls': json.dumps(walls),
        }

        form = BoardForm(form_data)
        if form.is_valid():
            cleaned_data = form.cleaned_data
            entrance = cleaned_data['entrance']
            exit = cleaned_data['exit']
            walls = cleaned_data['walls']

            me.board['entrance_position'] = entrance            
            me.board['exit_position'] = exit
            me.board['walls'] = walls
            me.ready = True
            me.save()

            if game.ready_players() > 1:
                me.board['player_position'] = opponent.board["entrance_position"]
                opponent.board['player_position'] = me.board["entrance_position"]

                me.save()
                opponent.save()
                game.game_stage = 2                
                game.save()

                channel_layer = get_channel_layer()
                async_to_sync(channel_layer.group_send)(
                    f'game_{game_id}',
                    {
                        'type': 'game_started',
                        'message': 'Game started'
                    }
                )
            else:
                channel_layer = get_channel_layer()
                async_to_sync(channel_layer.group_send)(
                    f'game_{game_id}',
                    {
                        'type': 'opponent_ready',
                        'message': 'Your opponent is ready'
                    }
                )


            return JsonResponse({'success': True}, status=200)
        else:
            return JsonResponse({'error': form.errors}, status=400)


class SendMessageView(View):
    def post(self, request, game_id, *args, **kwargs):
        game = get_object_or_404(Game, id=game_id)
        user, authorized = get_current_user(request)

        text = request.POST.get('text', '')

        if text:
            message = None
            if authorized:
                message = ChatMessage.objects.create(game=game, user=user, text=text)
            else:
                message = ChatMessage.objects.create(game=game, session_key=user, text=text)

            response_data = {
                'success': True,
                'chat_message': {
                    'session_key': user if not authorized else None,
                    'user': "Anonymous" if not authorized else message.user.username,
                    'text': message.text,
                    'created_at': message.created_at.isoformat(),
                }
            }
            return JsonResponse(response_data)

        return JsonResponse({'success': False})
    
class ExitMatchView(View):
    def get(self, request, code, *args, **kwargs):
        try:
            game = Game.objects.get(code=code)
        except:
            return JsonResponse({"success": False, "error": "Game not found"}, status=400)

        current_user, authorized= get_current_user(request)
        
        if not game.has_user(current_user):
            return JsonResponse({"success": False, "error": "You are not in this game"}, status=400)

        me, opponent = game.get_me_opponent(current_user)

        if game.player_1 == me:
            game.player_1 = None
        elif game.player_2 == me:
            game.player_2 = None

        me.delete()
        me = None
        game.save()

        if game.players() == 0 or game.game_stage == 2:
            if opponent:
                opponent.delete()
            game.delete()

            channel_layer = get_channel_layer()
            async_to_sync(channel_layer.group_send)(
                f'game_{game.id}',
                {
                    'type': 'player_exit',
                    'should_delete_game': True
                }
            )
        
        if game.players() > 0:
            game.notify_game_update('create')
            channel_layer = get_channel_layer()
            async_to_sync(channel_layer.group_send)(
                f'game_{game.id}',
                {
                    'type': 'player_exit',
                    'should_delete_game': False
                }
            )

        return JsonResponse({"success": True}, status=200)
        # return redirect(reverse("home"))
    

class JoinGame(View):
    def post(self, request, code, *args, **kwargs):
        game = get_object_or_404(Game, code=code)
        current_user, authorized = get_current_user(request)

        try:
            data = json.loads(request.body)
            room_password = data.get("password", None)
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON data'}, status=400)
        
        if game.has_user(current_user):
            return JsonResponse({"success": True}, status=200)

        if game.is_private and room_password != game.password:
            return JsonResponse({"success": False, "error": "Incorrect password!" + room_password}, status=400)
        
        if not game.player_1 or not game.player_2:
            player = None
            if authorized:
                player = Player.objects.create(user=current_user)
            else:
                player = Player.objects.create(session_key=current_user)
            
            if not game.player_1:                
                game.player_1 = player
            elif not game.player_2:
                game.player_2 = player
            
            game.save()
            game.notify_game_update('delete')
            channel_layer = get_channel_layer()
            async_to_sync(channel_layer.group_send)(
                f'game_{game.id}',
                {
                    'type': 'opponent_came',
                    'opponent': "Anonymous" if not authorized else current_user.username
                }
            )
            return JsonResponse({"success": True}, status=200)
        
        return JsonResponse({"success": False, "error": "You are not allowed to do this action!"}, status=400)
    
    def get(self, request, code, *args, **kwargs):
        game = get_object_or_404(Game, code=code)
        current_user, authorized = get_current_user(request)

        room_password = request.GET.get("password", None)

        if game.has_user(current_user):
            return redirect(reverse('game', args=[code]))

        if game.is_private and room_password != game.password:
            return redirect(reverse('home') + "?error=incorrect_password")
        
        if game.players() == 1:
            game.notify_game_update('delete') # не показывать эту игру на главной странице так как она заполнена

        if not game.player_1:
            player = Player.objects.create(user=current_user)
            game.player_1 = player
            game.save()
            return redirect(reverse('game', args=[code]))          
        elif not game.player_2:
            player = Player.objects.create(user=current_user)
            game.player_2 = player
            game.save()
            return redirect(reverse('game', args=[code]))

        return redirect(reverse('home') + "?error=game_full")



class MakeMoveView(View):
    def post(self, request, game_id):
        current_user, authorized = get_current_user(request)
        game = get_object_or_404(Game, id=game_id)
        me, opponent = game.get_me_opponent(current_user)

        if not game.has_user(current_user):
            return JsonResponse({'error': 'You are not allowed to make a move in this game.'}, status=403)            

        if not game.player_1.ready or not game.player_2.ready:
            return JsonResponse({'error': 'Both players must be ready to start the game.'}, status=400)
        
        if not me.current_turn:
            return JsonResponse({'error': 'Its not your turn.'}, status=400)

        try:
            data = json.loads(request.body)
            wanted_position = data.get('wanted_position')
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON data'}, status=400)

        current_position = me.board["player_position"]
        opponent_walls = opponent.board["walls"]

        game_ended = False
        winner = "Anonymous"

        # Проверка допустимости хода
        available_moves = get_available_moves(current_position, opponent_walls)
        if not available_moves:
            return JsonResponse({'error': 'Invalid move'}, status=400)
        
        channel_layer = get_channel_layer()
        opponent_user_id = opponent.user
        if not opponent_user_id:
            opponent_user_id = opponent.session_key
        else:
            opponent_user_id = opponent.user.id

        if can_move_to(current_position, wanted_position, opponent_walls):
            me.board["player_position"] = wanted_position
            success = True
            if wanted_position["x"] == opponent.board["exit_position"]["x"] and wanted_position["y"] == opponent.board["exit_position"]["y"]:
                game.is_active = False
                game_ended = True

                me.board["spotted_walls"] = opponent.board["walls"]
                me.current_turn = False
                opponent.board["spotted_walls"] = me.board["walls"]

                me.save()
                opponent.save()

                if me.user:
                    winner = str(me.user)
                game.winner = winner
                game.save()

                async_to_sync(channel_layer.group_send)(
                    f'game_{game_id}',
                    {
                        'type': 'game_ended',
                        'message': f'Game Finished! Winner is {winner}! Game will be deleted after 1 minute',                        
                        'winner': winner
                    }
                )

                def delete_game(game):
                    if game:
                        if game.player_1:
                            game.player_1.delete()
                        if game.player_2:
                            game.player_2.delete()
                        game.delete()
                # delete_game(game)

                # Поставить таймер на удаление игры через 1 минуту
                timer = threading.Timer(60.0, delete_game, [game])
                timer.start()
            
            async_to_sync(channel_layer.group_send)(
                f'user_{opponent_user_id}',
                {
                    'type': 'opponent_info',
                    'position': me.board["player_position"],
                    'can_go': [],
                    "turn_ended": False
                }
            )

        else:
            spotted_walls = me.board["spotted_walls"]
            spotted_walls.append([wanted_position["x"], wanted_position["y"], current_position["x"], current_position["y"]])
            me.board["spotted_walls"] = spotted_walls
            success = False
            me.current_turn = False
            opponent.current_turn = True
            opponent.save()
                    
            opponent_can_go = get_available_moves(opponent.board["player_position"], opponent.board["spotted_walls"])
            
            async_to_sync(channel_layer.group_send)(
                f'user_{opponent_user_id}',
                {
                    'type': 'opponent_info',
                    'position': me.board["player_position"],
                    'can_go': opponent_can_go,
                    'turn_ended': True
                }
            )

        me.save()
        
        available_moves = get_available_moves(me.board["player_position"], me.board["spotted_walls"])

        return JsonResponse({
            "success": success,
            "game_ended": game_ended,
            "can_go": available_moves,
            "spotted_walls": me.board["spotted_walls"],
            "player_position": me.board["player_position"],
            "player": str(me.user),
            "opponent": str(opponent.user),
        }, status=200)