from django.urls import path
from django.views.generic import RedirectView

from . import views

urlpatterns = [
    path('', RedirectView.as_view(url='dashboard', permanent=True), name='dashboard'),
    path('home', RedirectView.as_view(url='dashboard', permanent=True), name='dashboard'),
    path('dashboard', views.dashboard, name='dashboard'),

    #
    path('asset/<int:asset_id>/render.png', views.render_asset, name='render_asset'),
]
