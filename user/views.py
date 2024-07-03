from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from django.contrib.auth import login, authenticate, get_user_model
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views.generic import UpdateView

from user.forms import SignupForm, LoginForm, ProfileForm


User = get_user_model()


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


@method_decorator(login_required, name='dispatch')
class ProfileUpdateView(UpdateView):
    model = User
    form_class = ProfileForm
    template_name = 'user/profile.html'
    success_url = reverse_lazy('user:profile')

    def get_object(self, queryset=None):
        return self.request.user

    def form_valid(self, form):
        form.instance = self.request.user

        if 'avatar' in form.files:
            form.instance.avatar = form.files['avatar']

        return super().form_valid(form)
