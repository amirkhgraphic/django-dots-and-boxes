from django.contrib import admin
from django.contrib.admin import ModelAdmin, StackedInline
from django.urls import reverse
from django.utils.html import format_html

from utils.admin_mixin import DateListFilterMixin

from .models import Board, GameRoom, Square


class IsCompleteFilter(admin.SimpleListFilter):
    title = 'Is Complete'
    parameter_name = 'is_complete'

    def lookups(self, request, model_admin):
        return (
            ('Yes', 'Yes'),
            ('No', 'No'),
        )

    def queryset(self, request, queryset):
        value = self.value()
        if value == 'Yes':
            return queryset.filter(top=True, right=True, bottom=True, left=True)
        if value == 'No':
            return queryset.exclude(top=True, right=True, bottom=True, left=True)
        return queryset


@admin.register(Square)
class SquareAdmin(ModelAdmin, DateListFilterMixin):
    list_display = ('id', 'board_link', 'row', 'col', 'winner_link', 'is_complete', 'completed_at')
    readonly_fields = ('is_complete', 'completed_at')
    search_fields = ('row', 'col', 'winner')
    list_filter = (IsCompleteFilter, 'board')

    def winner_link(self, obj):
        if obj.winner:
            url = reverse("admin:user_user_change", args=[obj.winner.id])
            return format_html(
                '<a href="{}">{}</a>', url, obj.winner
            )
        return format_html(
            '-'
        )
    winner_link.short_description = 'Winner'

    def board_link(self, obj):
        url = reverse("admin:game_board_change", args=[obj.board.id])
        return format_html(
            '<a href="{}">{}</a>', url, obj.board
        )
    board_link.short_description = 'Board'


class SquareInline(admin.TabularInline):
    model = Square
    readonly_fields = ('is_complete', 'completed_at')
    extra = 0


@admin.register(Board)
class BoardAdmin(ModelAdmin, DateListFilterMixin):
    list_display = ('id', 'room_link', 'size', 'host_link', 'host_score', 'guest_link', 'guest_score', 'winner_link',
                    'created_at')
    readonly_fields = ('created_at',)
    list_filter = ('size', 'host', 'guest', 'winner')
    inlines = (SquareInline,)

    def room_link(self, obj):
        if obj.game_room:
            url = reverse("admin:game_gameroom_change", args=[obj.game_room.id])
            return format_html(
                '<a href="{}">{}</a>', url, obj.game_room.id
            )
        return format_html(
            '-'
        )
    room_link.short_description = 'Game Room'

    def host_link(self, obj):
        if obj.host:
            url = reverse("admin:user_user_change", args=[obj.host.id])
            return format_html(
                '<a href="{}">{}</a>', url, obj.host
            )
        return format_html(
            '-'
        )
    host_link.short_description = 'Host'

    def guest_link(self, obj):
        if obj.guest:
            url = reverse("admin:user_user_change", args=[obj.guest.id])
            return format_html(
                '<a href="{}">{}</a>', url, obj.guest
            )
        return format_html(
            '-'
        )
    guest_link.short_description = 'Guest'

    def winner_link(self, obj):
        if obj.winner:
            url = reverse("admin:user_user_change", args=[obj.winner.id])
            return format_html(
                '<a href="{}">{}</a>', url, obj.winner
            )
        return format_html(
            '-'
        )
    winner_link.short_description = 'Winner'


@admin.register(GameRoom)
class GameAdmin(ModelAdmin, DateListFilterMixin):
    list_display = ('id', 'board_link', 'host_link', 'guest_link', 'status', 'online_count')
    readonly_fields = ('online_count',)
    list_filter = ('board', 'player1', 'player2', 'status')

    def board_link(self, obj):
        url = reverse("admin:game_board_change", args=[obj.board.id])
        return format_html(
            '<a href="{}">{}</a>', url, obj.board
        )
    board_link.short_description = 'Board'

    def host_link(self, obj):
        if obj.player1:
            url = reverse("admin:user_user_change", args=[obj.player1.id])
            return format_html(
                '<a href="{}">{}</a>', url, obj.player2
            )
        return format_html(
            '-'
        )
    host_link.short_description = 'Host'

    def guest_link(self, obj):
        if obj.player2:
            url = reverse("admin:user_user_change", args=[obj.player2.id])
            return format_html(
                '<a href="{}">{}</a>', url, obj.player2
            )
        return format_html(
            '-'
        )
    guest_link.short_description = 'Guest'

    def online_count(self, obj):
        return obj.online_users.count()
    online_count.short_description = 'Online'
