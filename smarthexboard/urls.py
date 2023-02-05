from django.urls import path
from django.views.generic import RedirectView

from . import views

urlpatterns = [
    path('', RedirectView.as_view(url='home', permanent=True), name='index'),
    path('home', views.index, name='index'),

    path('tests', views.tests, name='tests'),
    path('generate_map', views.generate_map, name='generate_map'),
    path('generate_status/<str:map_uuid>/', views.generate_status, name='generate_status'),
    path('generated_map/<str:map_uuid>/', views.generated_map, name='generated_map'),

    path('styleguide', views.styleguide, name='styleguide'),
]
