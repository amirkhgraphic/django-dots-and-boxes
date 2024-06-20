from django.contrib.auth.decorators import login_required
from django.urls import path
from django.views.generic import TemplateView

from .views import create_room_view, delete_room_view, join_room_view, room_view

urlpatterns = [
    path('', login_required(TemplateView.as_view(template_name='game/create_join.html')), name='create-join'),
    path('room/create/', create_room_view, name='create-room'),
    path('room/delete/<int:room_id>/', delete_room_view, name='delete-room'),
    path('room/join/', join_room_view, name='join-room'),
    path('room/<int:room_id>/', room_view, name='room'),
]
