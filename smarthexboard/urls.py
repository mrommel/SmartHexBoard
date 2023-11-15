from django.urls import path
from django.views.generic import RedirectView

from . import views

urlpatterns = [
    path('', RedirectView.as_view(url='home', permanent=True), name='index'),
    path('home', views.index, name='index'),

    path('tests', views.tests, name='tests'),

    # map api
    # path('generate_map/<str:map_size>/<str:map_type>/', views.generate_map, name='generate_map'),
    # path('generate_status/<str:map_uuid>/', views.generate_status, name='generate_status'),
    # path('generated_map/<str:map_uuid>/', views.generated_map, name='generated_map'),

    # game api
    path('create_game', views.create_game, name='create_game'),
    path('generate_status/<str:game_uuid>/', views.generate_status, name='generate_status'),
    path('game_turn/<str:game_uuid>/', views.game_turn, name='game_turn'),

    # debug
    path('styleguide', views.styleguide, name='styleguide'),
]
