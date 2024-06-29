from django.contrib.auth import get_user_model
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required

from .models import GameRoom, Board, Square


User = get_user_model()


@login_required
def create_room_view(request):
    if request.method == 'POST':
        board_size = int(request.POST.get('board-size'))
        board = Board.objects.create(size=board_size)

        for i in range(1, board_size):
            for j in range(1, board_size):
                Square.objects.create(board=board, row=i, col=j)

        game_room = GameRoom.objects.create(board=board, player1=request.user)
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
        'username': request.user.username,
        'board_size': room.board.size,
    }

    return render(request, 'game/pvp-room.html', context)


@login_required
def create_pve_room(request):
    if request.method == 'POST':
        player = request.user
        bot = User.objects.get(username='bot')
        board_size = int(request.POST.get('board-size'))
        board = Board.objects.create(size=board_size, host=player, guest=bot)

        for i in range(1, board_size):
            for j in range(1, board_size):
                Square.objects.create(board=board, row=i, col=j)

        room = GameRoom.objects.create(player1=player, player2=bot, board=board)
        return redirect('game:pve-room', room_id=room.id)

    return render(request, 'game/pve.html')


@login_required
def pve_room_view(request, room_id):
    room = get_object_or_404(GameRoom, id=room_id)

    if request.user != room.player1:
        return redirect('home')

    context = {
        'room_id': room_id,
        'user': request.user,
        'bot': room.player2,
        'board_size': room.board.size,
    }

    return render(request, 'game/pve-room.html', context)