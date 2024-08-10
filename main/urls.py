from django.urls import path, include
from main.views import *

urlpatterns = [
    path('', HomePage.as_view(), name='home'),
    path('create-game/', CreateGame.as_view(), name='create_game'),
    path('game/<slug:code>/', GameView.as_view(), name='game'),
    
    path('game/<slug:code>/join/', JoinGame.as_view(), name='join_match'),
    path('game/<slug:code>/leave/', ExitMatchView.as_view(), name='exit_match'),
    path('update-game-stage/<int:game_id>/', UpdateGameStageView.as_view(), name='update_game_stage'),
    path('send_message/<int:game_id>/', SendMessageView.as_view(), name='send_message'),
    path('make_move/<int:game_id>/', MakeMoveView.as_view(), name='make_move'),

    path('login', LoginView.as_view(), name='login'),
    path('register', RegisterView.as_view(), name='register'),
    path('logout', LogoutView.as_view(), name='logout'),

]
