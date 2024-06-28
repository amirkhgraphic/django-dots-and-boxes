from django.contrib.auth.decorators import login_required
from django.urls import path
from django.views.generic import TemplateView

from .views import create_room_view, join_room_view, room_view, pve_room_view, create_pve_room

urlpatterns = [
    path('pvp/', login_required(TemplateView.as_view(template_name='game/pvp.html')), name='two-player'),
    path('pve/', create_pve_room, name='single-player'),
    path('pve/room/<int:room_id>/', pve_room_view, name='pve-room'),
    path('room/create/', create_room_view, name='create-room'),
    path('room/join/', join_room_view, name='join-room'),
    path('room/<int:room_id>/', room_view, name='room'),
]
