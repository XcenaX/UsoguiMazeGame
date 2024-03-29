from django.urls import path, include
from main.views import HomePage, GameView

urlpatterns = [
    path('', HomePage.as_view(), name='home'),
    path('game/<slug:code>/', GameView.as_view(), name='game'),

    path('accounts/', include('allauth.urls')),
]
