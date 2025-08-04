from django.urls import path
from django.views.generic import RedirectView

from . import views

urlpatterns = [
    path('', RedirectView.as_view(url='home', permanent=True), name='index'),
    path('home', views.index, name='index'),

    path('tests', views.tests, name='tests'),

    # game api
    path('create', views.game_create, name='game_create'),
    path('<str:game_id>/create/status', views.game_create_status, name='game_create_status'),
    path('<str:game_id>/map', views.game_map, name='game_map'),
    path('<str:game_id>/info', views.game_info, name='game_info'),
    path('<str:game_id>/update', views.game_update, name='game_update'),
    path('<str:game_id>/turn', views.game_turn, name='game_turn'),

    # game action api
    path('move_unit', views.game_move_unit, name='game_move_unit'),
    path('actions', views.game_actions, name='game_actions'),
    path('found_city', views.game_found_city, name='game_found_city'),
    path('city_info', views.game_city_info, name='game_city_info'),

    # debug
    path('styleguide', views.styleguide, name='styleguide'),
    path('city_view', views.city_view, name='city_view'),
]
