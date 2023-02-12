from django.db import models
from django.contrib.auth.base_user import AbstractBaseUser, BaseUserManager
from django.utils.crypto import get_random_string
from django.core.exceptions import ValidationError


class UserManager(BaseUserManager):
    def _create(self, first_name, email, password, **extra_fields):
        if not first_name:
            raise ValueError('User must have username')
        if not email:
            raise ValueError('User must have email')
        user = self.model(
            first_name=first_name,
            email=self.normalize_email(email),
            **extra_fields
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, first_name, email, password, **extra_fields):
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_active', False)
        return self._create(first_name, email, password, **extra_fields)

    def create_superuser(self, first_name, email, password, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_active', True)
        return self._create(first_name, email, password, **extra_fields)


class User(AbstractBaseUser):
    TYPE_CHOICES = [
        ('privat', 'Лично, частным образом'),
        ('professional', 'Лично, профессионально'),
        ('online', 'Онлайн'),
        ('other', 'Другое')
    ]
    AUDIENCE_CHOICES = [
        ('no aud', 'В настоящее время нет'),
        ('small aud', 'У меня маленькая аудитория'),
        ('normal aud', 'У меня достаточная аудитория')
    ]
    EXPERIENCE_CHOICES = [
        ('1+', 'Больше одного года'),
        ('5+', 'Больше пяти лет'),
        ('10+', 'Больше десяти лет')
    ]
    email = models.EmailField(max_length=255, unique=True)
    type_of_teach =  models.CharField(max_length=100, choices=TYPE_CHOICES, blank=True, null=True)
    experience = models.CharField(max_length=100, choices=EXPERIENCE_CHOICES, blank=True, null=True)
    audience = models.CharField(max_length=100, choices=AUDIENCE_CHOICES, blank=True, null=True)
    is_active = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    is_mentor = models.BooleanField(default=False)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    activation_code = models.CharField(max_length=8, blank=True)

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']

    def __str__(self) -> str:
        return self.first_name

    def has_module_perms(self, app_label):
        return self.is_staff

    def has_perm(self, obj=None):
        return self.is_staff

    def save(self,*args, **kwargs):
        if not self.first_name:
            raise ValidationError('Поле имени не может быть пустым!')
        super().save(*args, **kwargs)

    def create_activation_code(self):
        code = get_random_string(length=8)
        if User.objects.filter(activation_code=code).exists():
            self.create_activation_code()
        self.activation_code = code
        self.save()

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'


