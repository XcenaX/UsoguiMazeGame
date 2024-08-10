from django.urls import re_path, path
from main.consumers import ChatConsumer, GameConsumer

websocket_urlpatterns = [
    re_path(r'ws/game/(?P<game_id>\d+)/$', ChatConsumer.as_asgi()),
    path('ws/games/', GameConsumer.as_asgi()),
]