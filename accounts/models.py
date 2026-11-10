from django.db import models

from pathlib import Path
from uuid import uuid4

from django.conf import settings
from django.db import models


def avatar_upload_to(instance, filename):
    """avatars/user_5/3f2a...c1.jpg — уникальное имя, без кириллицы и пробелов."""
    return f"avatars/user_{instance.user_id}/{uuid4().hex}{Path(filename).suffix.lower()}"


class Profile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="profile",
        verbose_name="Пользователь",
    )
    position = models.CharField("Должность", max_length=150, blank=True)
    organization = models.CharField("Организация", max_length=200, blank=True)
    avatar = models.ImageField("Аватар", upload_to=avatar_upload_to, blank=True)

    class Meta:
        verbose_name = "Профиль"
        verbose_name_plural = "Профили"

    def __str__(self):
        return f"Профиль {self.user.get_username()}"