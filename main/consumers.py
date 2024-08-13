import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.core.wsgi import get_wsgi_application
import os
from maze.settings import MAX_MESSAGES_IN_CHAT

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'maze.settings')
application = get_wsgi_application()

from main.models import ChatMessage, Game

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user = self.scope['user']
        self.game_id = self.scope['url_route']['kwargs']['game_id']
        self.game_group_name = f'game_{self.game_id}'

        if self.user.id:
            self.user_group_name = f'user_{self.user.id}'
        else:
            session_key = self.scope['session'].session_key
            if not session_key:
                session_key = self.scope['session'].session_key = self.scope['session'].create()
            self.user_group_name = f'user_{session_key}'

        await self.channel_layer.group_add(
            self.game_group_name,
            self.channel_name
        )
        await self.channel_layer.group_add(
            self.user_group_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.game_group_name,
            self.channel_name
        )
        await self.channel_layer.group_discard(
            self.user_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message_data = text_data_json['message']

        user_session_key = None

        if self.scope['user'].id:
            user = self.scope['user']
        else:
            user = None
            message_data["user"] = "Anonymous"
            session_key = self.scope['session'].session_key
            if not session_key:
                session_key = self.scope['session'].session_key = self.scope['session'].create()
            user_session_key = session_key

        # Сохранение сообщения в базу данных
        game = await database_sync_to_async(Game.objects.get)(id=self.game_id)
        
        message = await database_sync_to_async(ChatMessage.objects.create)(
            game=game,
            user=user,
            session_key=user_session_key if not user else None,
            text=message_data['text']
        )

        await self.check_and_delete_old_messages(game, MAX_MESSAGES_IN_CHAT)

        message_data['created_at'] = message.created_at.isoformat()
        message_data['session_key'] = user_session_key

        await self.channel_layer.group_send(
            self.game_group_name,
            {
                'type': 'chat_message',
                'message': message_data
            }
        )

    async def chat_message(self, event):
        message = event['message']

        await self.send(text_data=json.dumps({
            'message': message,
            "type": "chat_message"
        }))

    async def player_exit(self, event):
        should_delete_game = event['should_delete_game']

        await self.send(text_data=json.dumps({
            'should_delete_game': should_delete_game,
            'exit': True
        }))
    
    async def opponent_came(self, event):
        opponent = event['opponent']

        await self.send(text_data=json.dumps({
            'opponent': opponent,
            'opponent_came': True
        }))

    async def opponent_ready(self, event):
        await self.send(text_data=json.dumps({            
            'opponent_ready': True
        }))

    async def game_started(self, event):
        message = event['message']

        await self.send(text_data=json.dumps({
            'message': message,
            'game_started': True
        }))

    async def opponent_info(self, event):
        position = event['position']
        can_go = event['can_go']
        turn_ended = event['turn_ended']
        await self.send(text_data=json.dumps({
            'opponent_position': position,
            'can_go': can_go,
            'turn_ended': turn_ended
        }))
    
    async def game_ended(self, event):
        message = event['message']
        winner = event['winner']
        await self.send(text_data=json.dumps({
            'message': message,
            'winner': winner,
            'game_ended': True
        }))

    @database_sync_to_async
    def check_and_delete_old_messages(self, game, max_messages):
        messages_count = ChatMessage.objects.filter(game=game).count()
        if messages_count > max_messages:
            ChatMessage.objects.filter(game=game).order_by('created_at').first().delete()


class GameConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.channel_layer.group_add(
            "games",
            self.channel_name
        )
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            "games",
            self.channel_name
        )

    async def send_game_update(self, event):
        await self.send(text_data=json.dumps(event["message"]))

    async def receive(self, text_data):
        # Обработка входящих сообщений, если требуется
        pass
