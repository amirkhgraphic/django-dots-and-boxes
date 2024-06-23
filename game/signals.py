from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import GameRoom


@receiver(post_save, sender=GameRoom)
def delete_game_room_if_player1_null(sender, instance, **kwargs):
    if instance.player1 is None:
        instance.delete()
        print('deleted in the signals')
