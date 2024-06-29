import json
import random
from time import sleep
from typing import Any, Coroutine

from asgiref.sync import sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth import get_user_model

from .models import GameRoom, Square
from log.models import Move


User = get_user_model()


class TwoPlayerRoomConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_name = int(self.scope['url_route']['kwargs']['room_name'])
        self.room_group_name = f'game_{self.room_name}'
        self.user = self.scope['user']
        self.username = str(self.user)
        self.avatar = self.scope['user'].avatar.url

        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.connect_user()
        self.role = await self.get_role()

        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'player_joined',
                'player': self.username,
                'avatar': self.avatar,
                'role': self.role
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
                await self.channel_layer.group_send(
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
                await self.delete_room()
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
                Move.objects.create(board=self.room.board, player=player, row=row, col=col, side=side)
                return 'complete'

            square.save()
            Move.objects.create(board=self.room.board, player=player, row=row, col=col, side=side)
            return 'done'

        except Square.DoesNotExist:
            return False

    @database_sync_to_async
    def check_game_over(self):
        return self.room.board.is_complete

    @database_sync_to_async
    def delete_room(self):
        self.room.delete()


class SinglePlayerRoomConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        room_name = int(self.scope['url_route']['kwargs']['room_name'])
        self.room_group_name = f'game_{room_name}'
        self.room = await sync_to_async(GameRoom.objects.get)(id=room_name)
        self.user = self.scope['user']
        self.bot = await self.get_bot()
        self.side_choices = await self.get_available_sides()

        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        await self.accept()

    async def receive(self, text_data=None, bytes_data=None):
        data = json.loads(text_data)
        action = data.get('action')

        if action == 'make_move':
            row, col, side = data['row'], data['col'], data['side']
            change_turn = await self.check_move(row, col, side, self.user)

            if change_turn is None:
                winner = await self.check_game_over()
                await self.channel_layer.group_send(
                    self.room_group_name,
                    {
                        'type': 'game_over',
                        'winner': str(winner),
                    }
                )

            # bot move
            elif change_turn:
                bot_row, bot_col, bot_side = random.choice(self.side_choices)
                change_turn = await self.check_move(bot_row, bot_col, bot_side, self.bot)

                while not change_turn:
                    if self.side_choices == []:
                        winner = await self.check_game_over()
                        await self.channel_layer.group_send(
                            self.room_group_name,
                            {
                                'type': 'game_over',
                                'winner': str(winner),
                            }
                        )
                        return

                    bot_row, bot_col, bot_side = random.choice(self.side_choices)
                    change_turn = await self.check_move(bot_row, bot_col, bot_side, self.bot)

    async def check_move(self, row, col, side, player):
        sides = ['top', 'right', 'bottom', 'left']
        second_side = {
            'top': lambda r, c: (r - 1, c),
            'right': lambda r, c: (r, c + 1),
            'bottom': lambda r, c: (r + 1, c),
            'left': lambda r, c: (r, c - 1),
        }
        squares = []
        change_turn = True

        result = await self.make_move(row, col, side, player)
        if not result:
            if player != self.bot:
                await self.channel_layer.group_send(
                    self.room_group_name,
                    {
                        'type': 'wrong_move',
                        'error': 'Invalid Move!',
                        'player': str(player),
                    }
                )
            return False

        if (row, col, side) in self.side_choices:
            self.side_choices.remove((row, col, side))

        if result == 'complete':
            squares.append({
                'row': row,
                'col': col,
            })
            change_turn = False

        row2, col2 = second_side[side](row, col)
        side2 = sides[(sides.index(side) + 2) % 4]
        result2 = await self.make_move(row2, col2, side2, player)

        if result2 == 'complete':
            squares.append({
                'row': row2,
                'col': col2,
            })
            change_turn = False

        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'game_move',
                'row': row,
                'col': col,
                'side': side,
                'squares': squares,
                'player': str(player),
                'change_turn': change_turn,
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
            change_turn = None
            await self.delete_room()

        return change_turn

    async def disconnect(self, code):
        await self.delete_room()
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    # Handlers
    async def wrong_move(self, event):
        await self.send(text_data=json.dumps({
            'type': 'wrong_move',
            'error': event['error'],
            'player': event['player'],
        }))

    async def game_move(self, event):
        await self.send(text_data=json.dumps({
            'type': 'game_move',
            'row': event['row'],
            'col': event['col'],
            'side': event['side'],
            'squares': event['squares'],
            'player': event['player'],
            'change_turn': event['change_turn'],
        }))

    async def game_over(self, event):
        await self.send(text_data=json.dumps({
            'type': 'game_over',
            'winner': event['winner'],
        }))

    # Database
    @database_sync_to_async
    def make_move(self, row, col, side, player):
        try:
            square = Square.objects.get(board__game_room=self.room, row=row, col=col)

            if getattr(square, side):
                return False

            setattr(square, side, True)
            # self.side_choices.remove((row, col, side))

            if square.is_complete:
                square.winner = player
                square.save()
                Move.objects.create(board=self.room.board, player=player, row=row, col=col, side=side)
                return 'complete'

            square.save()
            Move.objects.create(board=self.room.board, player=player, row=row, col=col, side=side)
            return 'done'

        except Square.DoesNotExist:
            print('not exist', row, col, player)
            return False

    @database_sync_to_async
    def check_game_over(self):
        return self.room.board.is_complete

    @database_sync_to_async
    def delete_room(self):
        self.room.delete()

    @database_sync_to_async
    def get_bot(self):
        return User.objects.get(username='bot')

    @database_sync_to_async
    def get_available_sides(self):
        n = self.room.board.size
        sides = []
        for i in range(1, n):
            for j in range(1, n):
                sides.append((i, j, 'left'))
                sides.append((i, j, 'top'))

                if j == n - 1:
                    sides.append((i, j, 'right'))

                if i == n - 1:
                    sides.append((i, j, 'bottom'))
        return sides
