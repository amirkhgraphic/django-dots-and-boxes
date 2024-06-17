from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from django.utils.decorators import method_decorator
from django.views.generic.edit import FormView, UpdateView
from django.contrib.auth import login, authenticate
from django.urls import reverse_lazy
from django.http import HttpResponseRedirect

from user.forms import User, SignupForm, LoginForm


def login_view(request):
    if request.method == 'POST':
        try:
            username = request.POST['username']
            user = User.objects.filter(email=username).first()

            if user:
                password_check = user.check_password(request.POST['password'])

                if password_check:
                    user = authenticate(username=username, password=request.POST['password'])
                    login(request, user)
                    messages.success(request, 'Login Successful!')
                    return redirect('home')

                else:
                    messages.error(request, 'Invalid Password!')

            else:
                messages.error(request, 'User does not exist.')
                return redirect('user:log-in')

        except Exception as problem:
            messages.error(request, problem)
            return redirect('user:log-in')

    form = LoginForm()
    context = {
        'title': 'Login',
        'form': form
    }
    return render(request, 'user/login.html', context=context)


def register_view(request):
    if request.method == 'POST':
        form = SignupForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Your account has been created')
            return redirect('user:log-in')
    else:
        form = SignupForm()
    context = {
        'title': 'Register',
        'form': form
    }
    return render(request, 'user/signup.html', context=context)

# class SignupView(FormView):
#     form_class = SignupForm
#     template_name = 'user/signup.html'
#     success_url = reverse_lazy('home')
#
#     def form_valid(self, form):
#         user = form.save(commit=False)
#         user.set_password(form.cleaned_data['password'])
#         user.avatar = form.cleaned_data['avatar']
#         user.save()
#         login(self.request, user)
#         if user is not None:
#             return HttpResponseRedirect(self.success_url)
#
#         return super().form_valid(form)


# class LoginView(FormView):
#     form_class = LoginForm
#     template_name = 'user/login.html'
#     success_url = reverse_lazy('home')
#
#     def form_valid(self, form):
#         user = authenticate(email=form.cleaned_data['email'],
#                             password=form.cleaned_data['password'])
#
#         if user is not None:
#             login(self.request, user)
#             return HttpResponseRedirect(self.success_url)
#
#         form.add_error(None, "Invalid email or password. Please try again.")
#         return self.form_invalid(form)
