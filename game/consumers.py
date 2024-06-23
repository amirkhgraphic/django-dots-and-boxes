import json
from typing import Any, Coroutine
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from .models import GameRoom, Square, Move


class GameRoomConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_name = int(self.scope['url_route']['kwargs']['room_name'])
        self.room_group_name = f'game_{self.room_name}'
        self.user = self.scope['user']

        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        await self.connect_user()
        role = await self.get_role()

        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'player_joined',
                'player': f'@{self.user.username}',
                'avatar': self.user.avatar.url,
                'role': role
            }
        )
        await self.accept()

    async def receive(self, text_data: Any = None, bytes_data: Any = None) -> Coroutine[Any, Any, None]:
        data = json.loads(text_data)
        action = data.get('action')

        if action == 'make_move':
            row, col, side, player = data['row'], data['col'], data['side'], self.user
            sides = ['top', 'right', 'bottom', 'left']
            second_side = {
                'top': lambda r, c: (r - 1, c),
                'right': lambda r, c: (r, c + 1),
                'bottom': lambda r, c: (r + 1, c),
                'left': lambda r, c: (r, c - 1),
            }

            result = await self.make_move(row, col, side, player)
            if not result:
                self.channel_layer.group_send(
                    self.room_group_name,
                    {
                        'type': 'wrong_move',
                        'error': 'Invalid Move!',
                        'player': str(player),
                    }
                )
                return

            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'game_move',
                    'row': row,
                    'col': col,
                    'side': side,
                    'player': str(player),
                }
            )

            if result == 'complete':
                await self.channel_layer.group_send(
                    self.room_group_name,
                    {
                        'type': 'square_complete',
                        'row': row,
                        'col': col,
                        'player': str(player),
                    }
                )

            row2, col2 = second_side[side](row, col)
            side2 = sides[(sides.index(side) + 2) % 4]
            result2 = await self.make_move(row2, col2, side2, player)

            if result2 == 'complete':
                await self.channel_layer.group_send(
                    self.room_group_name,
                    {
                        'type': 'square_complete',
                        'row': row2,
                        'col': col2,
                        'player': str(player),
                    }
                )

            winner = await self.check_game_over()
            if winner:
                await self.channel_layer.group_send(
                    self.room_group_name,
                    {
                        'type': 'game_over',
                        'winner': str(winner),
                    }
                )

        elif action == 'get_host':
            host = await self.get_host()
            if host:
                await self.channel_layer.group_send(
                    self.room_group_name,
                    {
                        'type': 'host_info',
                        'host': f'@{host.username}',
                        'avatar': host.avatar.url,
                    }
                )

    async def disconnect(self, close_code):
        if self.user:
            if self.user == self.room.player1:
                await self.channel_layer.group_send(
                    self.room_group_name,
                    {
                        'type': 'room_deleted',
                        'message': 'Room has been deleted by the host.',
                    }
                )
            else:

                await self.channel_layer.group_send(
                    self.room_group_name,
                    {
                        'type': 'player_left',
                        'player': f'@{self.user.username}',
                    }
                )

            await self.disconnect_user()
            await self.channel_layer.group_discard(
                self.room_group_name,
                self.channel_name
            )

    async def update_online_users_count(self):
        users = await self.online_users()
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'online_users_count',
                'count': len(users)
            }
        )

        if len(users) >= 2:
            host = await self.get_host()
            guest = users[0] if users[1] == host else users[1]
            turn = str(await self.get_player_turn())
            await self.set_board_players(host, guest)
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'start_game',
                    'host': str(host),
                    'guest': str(guest),
                    'player': str(self.user),
                    'turn': turn,
                }
            )
        else:
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'stop_game',
                }
            )

    '''Type Handlers'''
    async def player_joined(self, event):
        await self.update_online_users_count()
        await self.send(text_data=json.dumps({
            'type': 'player_joined',
            'player': event['player'],
            'avatar': event['avatar'],
            'role': event['role']
        }))

    async def online_users_count(self, event):
        await self.send(text_data=json.dumps({
            'type': 'online_users',
            'count': event['count']
        }))

    async def host_info(self, event):
        await self.send(text_data=json.dumps({
            'type': 'host_info',
            'player': event['host'],
            'avatar': event['avatar']
        }))

    async def player_left(self, event):
        await self.update_online_users_count()
        await self.send(text_data=json.dumps({
            'type': 'player_left',
            'player': event['player']
        }))

    async def room_deleted(self, event):
        await self.send(text_data=json.dumps({
            'type': 'room_deleted',
            'message': event['message'],
        }))
        await self.close()

    async def start_game(self, event):
        await self.send(text_data=json.dumps({
            'type': 'start_game',
            'host': event['host'],
            'guest': event['guest'],
            'current_player': event['player'],
            'current_turn': event['turn'],
        }))

    async def stop_game(self, event):
        await self.send(text_data=json.dumps({
            'type': 'stop_game',
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
            'player': event['player'],
        }))

    async def game_move(self, event):
        await self.send(text_data=json.dumps({
            'type': 'game_move',
            'row': event['row'],
            'col': event['col'],
            'side': event['side'],
            'player': event['player'],
        }))

    async def game_over(self, event):
        await self.send(text_data=json.dumps({
            'type': 'game_over',
            'winner': event['winner'],
        }))

    '''Database Modification Methods'''
    @database_sync_to_async
    def set_board_players(self, host, guest):
        self.room.board.host = host
        self.room.board.guest = guest
        self.room.board.save()

    @database_sync_to_async
    def get_role(self):
        return 'host' if self.user == self.room.player1 else 'guest'

    @database_sync_to_async
    def get_host(self):
        return self.room.player1

    @database_sync_to_async
    def get_guest(self):
        return self.room.player2

    @database_sync_to_async
    def get_player_turn(self):
        return self.room.player1 if self.room.board.turn == 'host' else self.room.player2

    @database_sync_to_async
    def change_turn(self):
        self.room.board.turn = 'host' if self.room.board.turn == 'guest' else 'guest'
        self.room.board.save()

    @database_sync_to_async
    def connect_user(self):
        self.room = GameRoom.objects.get(id=self.room_name)
        if self.user not in self.room.online_users.all():
            self.room.online_users.add(self.user)
            self.room.add_player(self.user)
            self.update_online_users_count()

    @database_sync_to_async
    def online_users(self):
        return [user for user in self.room.online_users.all()]

    @database_sync_to_async
    def disconnect_user(self):
        self.room.online_users.remove(self.user)
        self.room.player2 = None
        self.room.status = 'pending'
        self.room.save()

    @database_sync_to_async
    def make_move(self, row, col, side, player):
        try:
            square = Square.objects.get(board__game_room=self.room, row=row, col=col)

            if getattr(square, side):
                return False

            setattr(square, side, True)

            if square.is_complete:
                square.winner = player
                square.save()
                Move.objects.create(game_room=self.room, player=player, row=row, col=col, side=side)
                return 'complete'

            square.save()
            Move.objects.create(game_room=self.room, player=player, row=row, col=col, side=side)
            return 'done'

        except Square.DoesNotExist:
            return False

    @database_sync_to_async
    def check_game_over(self):
        return self.room.board.is_complete
