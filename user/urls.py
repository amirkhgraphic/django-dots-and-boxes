from django.urls import path
from django.contrib.auth import views as auth_views

from .views import authentication_view, login_view, signup_view

urlpatterns = [
    path('auth/', authentication_view, name='auth'),
    path('signup/', signup_view, name='sign-up'),
    path('login/', login_view, name='log-in'),
    path('logout/', auth_views.LogoutView.as_view(next_page='home'), name='log-out'),
]
