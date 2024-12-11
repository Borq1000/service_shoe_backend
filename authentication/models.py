from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager



class UserManager(BaseUserManager):
    def create_user(self, email, first_name, password=None, user_type='client', **extra_fields):
        if not email:
            raise ValueError('The Email must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, first_name=first_name, user_type=user_type, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('user_type', 'admin')
        first_name = extra_fields.pop('first_name', 'Admin')
        return self.create_user(email, first_name, password, **extra_fields)



class User(AbstractBaseUser, PermissionsMixin):
    USER_TYPE_CHOICES = (
        ('client', 'Client'),
        ('courier', 'Courier'),
        ('admin', 'Admin'),
    )

    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30, blank=True, null=True)
    phone = models.CharField(
        max_length=25,
        blank=True,
        null=True,
    )
    image = models.ImageField(
        upload_to='profile_images/%Y/%m/',
        null=True,
        blank=True,
        verbose_name='Фото профиля'
    )
    user_type = models.CharField(max_length=10, choices=USER_TYPE_CHOICES, default='client')
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'user_type']

    def __str__(self):
        return f"{self.email} ({self.user_type})"
