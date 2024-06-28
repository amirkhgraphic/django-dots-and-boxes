from django.urls import re_path
from .consumers import TwoPlayerRoomConsumer, SinglePlayerRoomConsumer

websocket_urlpatterns = [
    re_path(r'ws/two-player-room/(?P<room_name>\w+)/$', TwoPlayerRoomConsumer.as_asgi()),
    re_path(r'ws/single-player-room/(?P<room_name>\w+)/$', SinglePlayerRoomConsumer.as_asgi()),
]
