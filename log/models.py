from django.contrib.auth import get_user_model
from django.db import models

from game.models import Board

User = get_user_model()


class Move(models.Model):
    board = models.ForeignKey(Board, on_delete=models.CASCADE, related_name='moves')
    player = models.ForeignKey(User, on_delete=models.CASCADE, related_name='moves')
    row = models.IntegerField()
    col = models.IntegerField()
    side = models.CharField(max_length=10)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Move by {self.player} at ({self.row}, {self.col}) on {self.side}"