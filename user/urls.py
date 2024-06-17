from django.urls import path
from django.contrib.auth import views as auth_views

from .views import login_view, register_view

urlpatterns = [
    path('login/', login_view, name='log-in'),
    path('logout/', auth_views.LogoutView.as_view(), name='log-out'),
    path('signup/', register_view, name='sign-up'),

    # path('reset_password/', auth_views.PasswordResetView.as_view(
    #     template_name="user/reset_request.html"), name='reset_password'),
    # path('reset_password_sent/', auth_views.PasswordResetDoneView.as_view(
    #     template_name="user/reset_done.html"), name='password_reset_done'),
    # path('reset/<uidb64>/<token>', auth_views.PasswordResetConfirmView.as_view(
    #     template_name="user/reset_confirm.html"), name='password_reset_confirm'),
    # path('reset_password_complete/', auth_views.PasswordResetCompleteView.as_view(
    #     template_name="user/reset_complete.html"), name='password_reset_complete')
]
