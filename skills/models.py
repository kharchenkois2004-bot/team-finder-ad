from django.db import models


class Skill(models.Model):
    name = models.CharField(
        max_length=124,
        unique=True,
        verbose_name='Название'
    )

    class Meta:
        ordering = ['name']
        verbose_name = 'Навык'
        verbose_name_plural = 'Навыки'

    def __str__(self):
        return self.name
