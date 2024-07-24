from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django import forms

User = get_user_model()


class SignupForm(UserCreationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['avatar'].widget.attrs['class'] = 'form-control mb-2'
        self.fields['avatar'].widget.attrs['placeholder'] = 'upload your profile picture'

        self.fields['username'].widget.attrs['class'] = 'form-control mb-2'
        self.fields['username'].widget.attrs['placeholder'] = 'Choose a username'

        self.fields['email'].widget.attrs['class'] = 'form-control mb-2'
        self.fields['email'].widget.attrs['placeholder'] = 'Enter your email (optional)'

        self.fields['first_name'].widget.attrs['class'] = 'form-control mb-2'
        self.fields['first_name'].widget.attrs['placeholder'] = 'Enter your first name (optional)'

        self.fields['last_name'].widget.attrs['class'] = 'form-control mb-2'
        self.fields['last_name'].widget.attrs['placeholder'] = 'Enter your last name (optional)'

        self.fields['password1'].widget.attrs['class'] = 'form-control mb-2'
        self.fields['password1'].widget.attrs['placeholder'] = 'Enter a password'

        self.fields['password2'].widget.attrs['class'] = 'form-control mb-2'
        self.fields['password2'].widget.attrs['placeholder'] = 'Confirm your password'

    class Meta:
        model = User
        fields = ('avatar', 'username', 'email', 'first_name', 'last_name', 'password1', 'password2')


class LoginForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super(LoginForm, self).__init__(*args, **kwargs)

        self.fields['username'].widget.attrs['class'] = 'form-control mb-2'
        self.fields['username'].widget.attrs['placeholder'] = 'Username'

        self.fields['password'].widget.attrs['class'] = 'form-control mb-2'
        self.fields['password'].widget.attrs['placeholder'] = 'Password'


class ProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('avatar', 'username', 'email', 'first_name', 'last_name')
