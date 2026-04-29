import io
import os
import random

from django.conf import settings
from django.core.files.base import ContentFile
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.db import models
from PIL import Image, ImageDraw, ImageFont

from skills.models import Skill
from team_finder.constants import COLORS, IMG_SIZE, TEXTBBOX_XY, NAME_LENGTH
from team_finder.constants import USER_ABOUT_LENGTH, USER_PHONE_LENGTH
from users.managers import UserManager


def user_avatar_path(instance, filename):
    return f'avatars/user_{instance.id}/{filename}'


class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(
        unique=True,
        verbose_name='Email'
        )
    name = models.CharField(
        max_length=NAME_LENGTH,
        verbose_name='Имя'
        )
    surname = models.CharField(
        max_length=NAME_LENGTH,
        verbose_name='Фамилия'
        )
    avatar = models.ImageField(
        upload_to=user_avatar_path,
        verbose_name='Аватар'
        )
    phone = models.CharField(
        max_length=USER_PHONE_LENGTH,
        verbose_name='Телефон'
        )
    github_url = models.URLField(
        blank=True,
        verbose_name='Ссылка на GitHub'
        )
    about = models.TextField(
        max_length=USER_ABOUT_LENGTH,
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
        bg_color = random.choice(COLORS)

        img = Image.new('RGB', IMG_SIZE, color=bg_color)
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

        bbox = draw.textbbox(TEXTBBOX_XY, first_letter, font=font)
        w, h = bbox[2]-bbox[0], bbox[3]-bbox[1]
        draw.text(
            ((IMG_SIZE[0]-w)/2, (IMG_SIZE[1]-h)/2-10),
            first_letter,
            fill='white',
            font=font
            )

        buffer = io.BytesIO()
        img.save(buffer, format='PNG')
        buffer.seek(0)
        self.avatar.save(
            f'default_{self.pk}.png',
            ContentFile(buffer.read()),
            save=False
            )
        super().save(update_fields=['avatar'])
