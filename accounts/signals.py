from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import Profile


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def ensure_profile(sender, instance, created, raw=False, **kwargs):
    """Создаёт профиль новому пользователю. Пользователям, созданным раньше
    (например, суперпользователю), профиль создаётся при следующем сохранении,
    в том числе при входе (обновляется last_login)."""
    if raw:
        return
    Profile.objects.get_or_create(user=instance)