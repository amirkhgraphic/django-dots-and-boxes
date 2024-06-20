import asyncio
import json
from typing import Any, Coroutine

from asgiref.sync import sync_to_async, async_to_sync
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from .models import GameRoom, Square, Move


class GameRoomConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_name = int(self.scope['url_route']['kwargs']['room_name'])
        self.room_group_name = f'game_{self.room_name}'
        self.user = self.scope['user']
        self.count = 0

        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        await self.accept()
        await self.connect_user()

        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'player_joined',
                'player': f'@{self.user.username}',
            }
        )

    @database_sync_to_async
    def connect_user(self):
        self.room = GameRoom.objects.get(id=self.room_name)
        if self.user not in self.room.online_users.all():
            self.room.online_users.add(self.user)
            self.update_online_users_count()

    @database_sync_to_async
    def disconnect_user(self):
        self.room.online_users.remove(self.user)
        self.update_online_users_count()

    async def player_joined(self, event):
        await self.update_online_users_count()
        await self.send(text_data=json.dumps({
            'type': 'player_joined',
            'player': event['player'],
        }))

    async def disconnect(self, close_code):
        if self.user:
            await self.disconnect_user()
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'player_left',
                    'player': f'@{self.user.username}',
                }
            )

        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def player_left(self, event):
        await self.update_online_users_count()
        await self.send(text_data=json.dumps({
            'type': 'player_left',
            'player': event['player']
        }))

    async def update_online_users_count(self):
        self.count = await self.online_users()
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'online_users_count',
                'count': self.count
            }
        )

        if self.count == 2:
            host, guest, size = await self.get_start_data()
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'start_game',
                    'host': host,
                    'guest': guest,
                    'size': size,
                }
            )

    @database_sync_to_async
    def online_users(self):
        return self.room.online_users.count()

    async def online_users_count(self, event):
        await self.send(text_data=json.dumps({
            'type': 'online_users',
            'count': event['count']
        }))

    @database_sync_to_async
    def get_start_data(self):
        return [user.username for user in self.room.online_users.all()] + [self.room.board.size]

    async def start_game(self, event):
        await self.send(text_data=json.dumps({
            'type': 'start_game',
            'host': event['host'],
            'guest': event['guest'],
            'size': event['size']
        }))

    async def receive(self, text_data: Any = None, bytes_data: Any = None) -> Coroutine[Any, Any, None]:
        data = json.loads(text_data)
        action = data['action']

        if action == 'make_move':
            row = data['row']
            col = data['col']
            side = data['side']
            player = self.user
            await self.make_move(row, col, side, player)

    @database_sync_to_async
    def make_move(self, row, col, side, player):
        def mark_side(i, j, s=side):
            try:
                square = Square.objects.get(board__game_room=game_room, row=i, col=j)

                if getattr(square, s):
                    return False

                setattr(square, s, True)
                if square.is_complete:
                    square.winner = player
                    self.channel_layer.group_send(
                        self.room_group_name,
                        {
                            'type': 'square_complete',
                            'row': i,
                            'col': j,
                            'side': s,
                            'player': player.username,
                        }
                    )
                square.save()
                Move.objects.create(game_room=game_room, player=player, row=i, col=j, side=s)
                return True

            except Square.DoesNotExist:
                return False

        game_room = GameRoom.objects.get(id=self.room_name)
        sides = ['top', 'right', 'bottom', 'left']
        sides_action = {
            'top': lambda r, c: (r - 1, c),
            'right': lambda r, c: (r, c + 1),
            'bottom': lambda r, c: (r + 1, c),
            'left': lambda r, c: (r, c - 1),
        }

        # mark all the side that are the same:
        if mark_side(row, col):
            r, c = sides_action[side]
            mark_side(r, c, s=sides[(sides.index(side) + 2) % 4])

            self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'game_move',
                    'row': row,
                    'col': col,
                    'side': side,
                    'player': player.username,
                }
            )

        else:  # on error...
            error = 'Invalid Move!'

            self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'wrong_move',
                    'error': error,
                    'player': player.username,
                }
            )

    async def game_move(self, event):
        await self.send(text_data=json.dumps({
            'type': 'game_move',
            'row': event['row'],
            'col': event['col'],
            'side': event['side'],
            'player': event['player'],
        }))

    async def wrong_move(self, event):
        await self.send(text_data=json.dumps({
            'type': 'wrong_move',
            'error': event['error'],
            'player': event['player'],
        }))

    async def square_complete(self, event):
        await self.send(text_data=json.dumps({
            'type': 'square_complete',
            'row': event['row'],
            'col': event['col'],
            'side': event['side'],
            'player': event['player'],
        }))
