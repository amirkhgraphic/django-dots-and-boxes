from django.contrib import admin
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.utils.html import format_html

from game.models import Board
from django.contrib.auth.admin import UserAdmin
from django.utils.translation import gettext_lazy as _

from utils.admin_mixin import DateListFilterMixin


User = get_user_model()


class HostBoardInline(admin.StackedInline):
    fk_name = 'host'
    model = Board
    extra = 0
    verbose_name = 'Host Game'


class GuestBoardInline(admin.StackedInline):
    fk_name = 'guest'
    model = Board
    extra = 0
    verbose_name = 'Guest Game'


@admin.register(User)
class MyUserAdmin(UserAdmin, DateListFilterMixin):
    list_display = ('user_link', 'render_avatar', 'created_at', 'last_login', 'is_active', 'is_staff')
    readonly_fields = ('render_avatar', 'created_at', 'updated_at', 'last_login')
    inlines = (HostBoardInline, GuestBoardInline)
    search_fields = ('username', )
    ordering = ('-created_at',)
    fieldsets = (
        (_('basic'), {'fields': (('render_avatar', 'avatar'), 'username')}),
        (_('Important dates'), {'fields': ('created_at', 'updated_at', 'last_login')}),
        (_('Permissions'), {'fields': ('is_staff', 'is_active')}),
    )

    add_fieldsets = (
        ('Required Fields', {
            'classes': ('wide',),
            'fields': ('username', 'password1', 'password2'),
        }),
        ('Optional Fields', {
            'classes': ('wide',),
            'fields': ('avatar', 'is_active', 'is_staff'),
        }),
    )

    def user_link(self, obj):
        url = reverse("admin:user_user_change", args=[obj.id])
        return format_html(
            '<a href="{}">{}</a>', url, obj
        )
    user_link.short_description = 'User'

    def render_avatar(self, obj):
        return format_html(
            f'<img src="{obj.avatar.url}" width="50px" style="max-height:50px;" />'
        )
    render_avatar.short_description = 'Profile Image'

    def delete_queryset(self, request, queryset):
        for obj in queryset:
            obj.delete()
        super().delete_queryset(request, queryset)
