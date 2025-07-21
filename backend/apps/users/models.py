from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _
from backend.apps.users.manager import CustomUserManager

class User(AbstractUser):
    username = None 
    email = models.EmailField(_("email address"), unique=True)
    full_name = models.CharField(_("full name"), max_length=150)
    dietary_restrictions = models.TextField(blank=True)

    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['full_name']

    class Meta:
        verbose_name = _("user")
        verbose_name_plural = _("users")
        ordering = ['email']

    def __str__(self):
        return self.full_name or self.email
