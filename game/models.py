from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class Board(models.Model):
    PLAYER_CHOICES = [
        ('host', 'Host'),
        ('guest', 'Guest'),
    ]

    size = models.IntegerField()
    host = models.ForeignKey(User, on_delete=models.CASCADE, related_name='host_games', null=True, blank=True)
    guest = models.ForeignKey(User, on_delete=models.CASCADE, related_name='guest_games', null=True, blank=True)
    turn = models.CharField(max_length=7, choices=PLAYER_CHOICES, default='host')
    winner = models.CharField(max_length=7, choices=PLAYER_CHOICES, null=True, blank=True)

    def __str__(self):
        return f"Board {self.id} ({self.size}x{self.size})"

    @property
    def is_complete(self):
        scores = {
            self.host: 0,
            self.guest: 0,
        }

        for square in self.squares.all():
            if not square.is_complete:
                return False
            scores[square.winner] += 1

        if scores[self.host] == scores[self.guest]:
            return 'Draw'
        elif scores[self.host] > scores[self.guest]:
            return str(self.host)

        return str(self.guest)


class Square(models.Model):
    board = models.ForeignKey(Board, on_delete=models.CASCADE, related_name='squares')
    row = models.IntegerField()
    col = models.IntegerField()
    top = models.BooleanField(default=False)
    left = models.BooleanField(default=False)
    right = models.BooleanField(default=False)
    bottom = models.BooleanField(default=False)
    winner = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='won_squares')

    @property
    def is_complete(self) -> bool:
        return self.top and self.right and self.bottom and self.left

    class Meta:
        unique_together = ('board', 'row', 'col')

    def __str__(self):
        return f"Square ({self.row}, {self.col}) on Board {self.board.id}"


class GameRoom(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('playing', 'Playing'),
        ('complete', 'Complete'),
    ]

    board = models.OneToOneField(Board, on_delete=models.CASCADE, related_name='game_room')
    player1 = models.ForeignKey(User, on_delete=models.CASCADE, related_name='player1_games', null=True, blank=True)
    player2 = models.ForeignKey(User, on_delete=models.CASCADE, related_name='player2_games', null=True, blank=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    online_users = models.ManyToManyField(User, related_name='online_in_groups', blank=True)

    def __str__(self):
        return f"GameRoom {self.id} - {self.status}"

    @property
    def is_full(self) -> bool:
        return self.player1 and self.player2

    def add_player(self, player):
        if self.player1 is None:
            self.player1 = player
            self.save()

        elif self.player2 is None and self.player1 != player:
            self.player2 = player
            self.status = 'playing'
            self.save()

    def end_game(self, winner):
        self.status = 'complete'
        self.winner = winner
        self.save()


class Move(models.Model):
    game_room = models.ForeignKey(GameRoom, on_delete=models.CASCADE, related_name='moves')
    player = models.ForeignKey(User, on_delete=models.CASCADE)
    row = models.IntegerField()
    col = models.IntegerField()
    side = models.CharField(max_length=10)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Move by {self.player} at ({self.row}, {self.col}) on {self.side}"
