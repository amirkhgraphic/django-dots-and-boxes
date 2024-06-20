from django.contrib import admin
from .models import Board, GameRoom, Square, Move

admin.site.register(GameRoom)
admin.site.register(Board)
admin.site.register(Square)
admin.site.register(Move)
