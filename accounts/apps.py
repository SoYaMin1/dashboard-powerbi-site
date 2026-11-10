from django.apps import AppConfig

from django.apps import AppConfig

class AccountsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "accounts"
    verbose_name = "Пользователи и профили"

    def ready(self):
        from . import signals  # noqa: F401