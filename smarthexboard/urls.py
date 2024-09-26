from django.urls import path
from django.views.generic import RedirectView

from . import views

urlpatterns = [
    path('', RedirectView.as_view(url='home', permanent=True), name='index'),
    path('home', views.index, name='index'),

    path('tests', views.tests, name='tests'),

    # game api
    path('game/create', views.game_create, name='game_create'),
    path('game/<str:game_uuid>/create/status', views.game_create_status, name='game_create_status'),
    path('game/<str:game_uuid>/map', views.game_map, name='game_map'),
    path('game/<str:game_uuid>/info', views.game_info, name='game_info'),
    path('game/<str:game_uuid>/update', views.game_update, name='game_update'),
    path('game/<str:game_uuid>/turn', views.game_turn, name='game_turn'),

    # game action api
    path('game/<str:game_uuid>/move/from/<str:old_location>/to/<str:new_location>', views.game_move_unit, name='game_move_unit'),
    # found city at
    # open city

    # debug
    path('styleguide', views.styleguide, name='styleguide'),
]
