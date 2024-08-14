from django.urls import path, include
import main.views as main_views

urlpatterns = [
    path('', main_views.HomePage.as_view(), name='home'),
    path('create-game/', main_views.CreateGame.as_view(), name='create_game'),
    path('quick-join-game/', main_views.QuickJoin.as_view(), name='quick_join'),
    path('game/<slug:code>/', main_views.GameView.as_view(), name='game'),
    
    path('game/<slug:code>/join/', main_views.JoinGame.as_view(), name='join_match'),
    path('game/<slug:code>/leave/', main_views.ExitMatchView.as_view(), name='exit_match'),
    path('update-game-stage/<int:game_id>/', main_views.UpdateGameStageView.as_view(), name='update_game_stage'),
    path('send_message/<int:game_id>/', main_views.SendMessageView.as_view(), name='send_message'),
    path('make_move/<int:game_id>/', main_views.MakeMoveView.as_view(), name='make_move'),

    path('login', main_views.LoginView.as_view(), name='login'),
    path('register', main_views.RegisterView.as_view(), name='register'),
    path('logout', main_views.LogoutView.as_view(), name='logout'),

]
