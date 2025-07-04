from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models

class CustomUserManager(BaseUserManager):
    use_in_migrations = True

    def create_user(self, username, email=None, password=None, **extra_fields):
        if not username:
            raise ValueError('Nome utente obbligatorio')
        if not email:
            raise ValueError('Email obbligatoria')
        if not password:
            raise ValueError('Password obbligatoria')
        email = self.normalize_email(email)
        user = self.model(username=username, email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, email=None, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser deve avere is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser deve avere is_superuser=True.')

        return self.create_user(username, email, password, **extra_fields)

class CustomUser(AbstractUser):
    birth_date = models.DateField(null=True, blank=True)
    is_premium = models.BooleanField(default=False)

    objects = CustomUserManager()

    def __str__(self):
        return self.username