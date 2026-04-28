from django.db import models

from team_finder.constants import NAME_LENGTH


class Skill(models.Model):
    name = models.CharField(
        max_length=NAME_LENGTH,
        unique=True,
        verbose_name='Название'
    )

    class Meta:
        ordering = ['name']
        verbose_name = 'Навык'
        verbose_name_plural = 'Навыки'

    def __str__(self):
        return self.name
