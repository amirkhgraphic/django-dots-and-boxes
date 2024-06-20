from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required

from .models import GameRoom, Board, Square


@login_required
def create_room_view(request):
    if request.method == 'POST':
        board_size = int(request.POST.get('board-size'))
        board = Board.objects.create(size=board_size)

        for i in range(1, board_size):
            for j in range(1, board_size):
                Square.objects.create(board=board, row=i, col=j)

        game_room = GameRoom.objects.create(board=board)
        game_room.add_player(request.user)
        return redirect('game:room', room_id=game_room.id)

    return render(request, 'game/create_room.html')


@login_required
def join_room_view(request):
    if request.method == 'POST':
        room_id = request.POST['room_id']

        if not GameRoom.objects.filter(id=room_id).exists():
            return render(request, 'game/join_room.html', {'error': f'Room {room_id} doesn\'t exists!'})

        room = GameRoom.objects.get(id=room_id)

        if request.user not in [room.player1, room.player2]:
            if room.is_full:
                return render(request, 'game/join_room.html', {'error': 'Room is full'})
            else:
                room.add_player(request.user)

        return redirect('game:room', room_id=room_id)

    return render(request, 'game/join_room.html')


@login_required
def room_view(request, room_id):
    room = get_object_or_404(GameRoom, id=room_id)

    if request.user not in [room.player1, room.player2]:
        return redirect('game:join-room')

    context = {
        'room_id': room_id,
        'user_id': request.user.id,
        'board_size': room.board.size,
    }

    return render(request, 'game/room.html', context)


@login_required
def delete_room_view(request, room_id):
    room = get_object_or_404(GameRoom, id=room_id)

    if request.user.id != room.player1:
        room.delete()

    return redirect('game:create-join')
