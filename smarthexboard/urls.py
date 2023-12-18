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
    path('game/create', views.game_create, name='game_create'),
    path('game/<str:game_uuid>/create/status', views.game_create_status, name='game_create_status'),
    path('game/<str:game_uuid>/map', views.game_map, name='game_map'),
    path('game/<str:game_uuid>/info', views.game_info, name='game_info'),
    path('game/<str:game_uuid>/update', views.game_update, name='game_update'),
    path('game/<str:game_uuid>/turn', views.game_turn, name='game_turn'),

    # debug
    path('styleguide', views.styleguide, name='styleguide'),
]
