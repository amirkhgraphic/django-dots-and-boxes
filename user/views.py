from django.contrib import messages
from django.shortcuts import redirect, render
from django.contrib.auth import login, authenticate

from user.forms import SignupForm, LoginForm


def login_view(request):
    if request.method == 'POST':
        login_form = LoginForm(request, data=request.POST)
        if login_form.is_valid():
            username = login_form.cleaned_data['username']
            password = login_form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            if user:
                login(request, user)
                return redirect('home')
    else:
        login_form = LoginForm()

    signup_form = SignupForm()
    context = {
        'title': 'Authentication',
        'signup_form': signup_form,
        'login_form': login_form
    }
    return render(request, 'user/authenticataion-page.html', context=context)


def signup_view(request):
    if request.method == 'POST':
        signup_form = SignupForm(request.POST, request.FILES)
        if signup_form.is_valid():
            signup_form.save()
            messages.success(request, 'Your account has been created!')

            username = signup_form.cleaned_data['username']
            raw_password = signup_form.cleaned_data['password1']
            user = authenticate(request, username=username, password=raw_password)
            if user is not None:
                login(request, user)
                return redirect('home')
        else:
            messages.error(request, 'Authentication failed. Please try logging in manually.')
    else:
        signup_form = SignupForm()

    login_form = LoginForm()
    context = {
        'title': 'Authentication',
        'signup_form': signup_form,
        'login_form': login_form
    }
    return render(request, 'user/authenticataion-page.html', context=context)


def authentication_view(request):
    signup_form = SignupForm()
    login_form = LoginForm()
    context = {
        'title': 'Authentication',
        'signup_form': signup_form,
        'login_form': login_form
    }
    return render(request, 'user/authenticataion-page.html', context=context)
