from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.utils.translation import gettext_lazy as _
from django.db import models


class CustomUserManager(BaseUserManager):
    def create_user(self, username, password, **other_fields):
        user = self.model(username=username, **other_fields)
        user.set_password(password)

        user.save()
        return user

    def create_superuser(self, username, password, **other_fields):
        other_fields.setdefault('is_staff', True)
        other_fields.setdefault('is_superuser', True)

        return self.create_user(username, password, **other_fields)


class User(AbstractBaseUser, PermissionsMixin):
    avatar = models.ImageField(default='avatar/default.png', upload_to='avatar/')
    username = models.CharField(max_length=255, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    objects = CustomUserManager()

    USERNAME_FIELD = 'username'

    def __str__(self):
        return f"@{self.username}"
