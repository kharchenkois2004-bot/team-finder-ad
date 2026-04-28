from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.contrib.auth.models import PermissionsMixin
from django.db import models
from skills.models import Skill
import os
from PIL import Image, ImageDraw, ImageFont
import random
from django.conf import settings


class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('Email обязателен')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(email, password, **extra_fields)


def user_avatar_path(instance, filename):
    return f'avatars/user_{instance.id}/{filename}'


class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(
        unique=True,
        verbose_name='Email'
        )
    name = models.CharField(
        max_length=124,
        verbose_name='Имя'
        )
    surname = models.CharField(
        max_length=124,
        verbose_name='Фамилия'
        )
    avatar = models.ImageField(
        upload_to=user_avatar_path,
        verbose_name='Аватар'
        )
    phone = models.CharField(
        max_length=12,
        verbose_name='Телефон'
        )
    github_url = models.URLField(
        blank=True,
        verbose_name='Ссылка на GitHub'
        )
    about = models.TextField(
        max_length=256,
        blank=True,
        verbose_name='О себе'
        )
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    skills = models.ManyToManyField(
        Skill,
        blank=True,
        related_name='users'
        )

    favorites = models.ManyToManyField(
        'projects.Project',
        blank=True,
        related_name='interested_users'
    )

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name', 'surname']

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return f'{self.name} {self.surname}'

    def save(self, *args, **kwargs):
        is_new = self.pk is None
        super().save(*args, **kwargs)
        if is_new and not self.avatar:
            self.generate_default_avatar()

    def generate_default_avatar(self):
        first_letter = self.name[0].upper() if self.name else '?'
        colors = [
            (52, 152, 219),
            (46, 204, 113),
            (155, 89, 182),
            (52, 73, 94),
            (241, 196, 15),
            (230, 126, 34),
            (231, 76, 60),
            (149, 165, 166)
        ]
        bg_color = random.choice(colors)
        img_size = (200, 200)
        img = Image.new('RGB', img_size, color=bg_color)
        draw = ImageDraw.Draw(img)

        font = None
        font_relative_path = 'fonts/Neue_Haas_Grotesk_Display_Pro_75_Bold.otf'

        for static_dir in settings.STATICFILES_DIRS:
            font_path = os.path.join(static_dir, font_relative_path)
            if os.path.exists(font_path):
                font = ImageFont.truetype(font_path, 100)
                break

        if font is None:
            font = ImageFont.load_default()

        bbox = draw.textbbox((0, 0), first_letter, font=font)
        w, h = bbox[2]-bbox[0], bbox[3]-bbox[1]
        draw.text(
            ((img_size[0]-w)/2, (img_size[1]-h)/2-10),
            first_letter,
            fill='white',
            font=font
            )

        from django.core.files.base import ContentFile
        import io
        buffer = io.BytesIO()
        img.save(buffer, format='PNG')
        buffer.seek(0)
        self.avatar.save(
            f'default_{self.pk}.png',
            ContentFile(buffer.read()),
            save=False
            )
        super().save(update_fields=['avatar'])
