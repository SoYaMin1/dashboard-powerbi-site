"""Настройки проекта AdventureWorks Sales Analytics.

Все секреты и параметры окружения читаются из .env / переменных окружения.
"""
import os
import sys
from pathlib import Path
from urllib.parse import quote_plus

import dj_database_url
from django.contrib.messages import constants as message_constants
from django.core.exceptions import ImproperlyConfigured
from django.utils.csp import CSP
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")


def env_bool(name, default=False):
    value = os.getenv(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


def env_list(name, default=""):
    return [item.strip() for item in os.getenv(name, default).split(",") if item.strip()]


TESTING = len(sys.argv) > 1 and sys.argv[1] == "test"

# --- Основное -----------------------------------------------------------------
DEBUG = env_bool("DEBUG", False)

SECRET_KEY = os.getenv("SECRET_KEY")
if not SECRET_KEY:
    if DEBUG or TESTING:
        SECRET_KEY = "django-insecure-local-dev-only"  # только для локальной разработки
    else:
        raise ImproperlyConfigured("Задайте SECRET_KEY в .env или в переменных окружения.")

ALLOWED_HOSTS = env_list("ALLOWED_HOSTS", "localhost,127.0.0.1")
CSRF_TRUSTED_ORIGINS = env_list("CSRF_TRUSTED_ORIGINS")

# Render сам выставляет RENDER_EXTERNAL_HOSTNAME (например, mysite.onrender.com)
RENDER_EXTERNAL_HOSTNAME = os.getenv("RENDER_EXTERNAL_HOSTNAME")
if RENDER_EXTERNAL_HOSTNAME:
    ALLOWED_HOSTS.append(RENDER_EXTERNAL_HOSTNAME)
    CSRF_TRUSTED_ORIGINS.append(f"https://{RENDER_EXTERNAL_HOSTNAME}")

# --- Приложения ---------------------------------------------------------------
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "whitenoise.runserver_nostatic",
    "django.contrib.staticfiles",
    # Проектные приложения
    "core",
    "accounts",
    "dashboards",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "django.middleware.csp.ContentSecurityPolicyMiddleware",
]

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "core.context_processors.site_contacts",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"

# --- База данных: SQLite локально, PostgreSQL на Render (DATABASE_URL) --------
DATABASES = {
    "default": dj_database_url.config(
        default=f"sqlite:///{BASE_DIR / 'db.sqlite3'}",
        conn_max_age=600,
    )
}

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# --- Язык и время --------------------------------------------------------------
LANGUAGE_CODE = "ru"
TIME_ZONE = "Asia/Bishkek"
USE_I18N = True
USE_TZ = True

# --- Статика и медиа ------------------------------------------------------------
STATIC_URL = "static/"
STATICFILES_DIRS = [BASE_DIR / "static"]
STATIC_ROOT = BASE_DIR / "staticfiles"

MEDIA_URL = "media/"
MEDIA_ROOT = BASE_DIR / "media"

STORAGES = {
    "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
    "staticfiles": {
        # В разработке и тестах обычное хранилище, в продакшене WhiteNoise со сжатием и хешами
        "BACKEND": (
            "django.contrib.staticfiles.storage.StaticFilesStorage"
            if DEBUG or TESTING
            else "whitenoise.storage.CompressedManifestStaticFilesStorage"
        ),
    },
}

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# --- Авторизация -----------------------------------------------------------------
LOGIN_URL = "accounts:login"
LOGIN_REDIRECT_URL = "dashboards:list"
LOGOUT_REDIRECT_URL = "core:home"
# Вход по имени пользователя ИЛИ по email
AUTHENTICATION_BACKENDS = ["accounts.backends.EmailOrUsernameBackend"]

# --- Почта: в разработке письма выводятся в консоль --------------------------------
EMAIL_BACKEND = os.getenv("EMAIL_BACKEND", "django.core.mail.backends.console.EmailBackend")
DEFAULT_FROM_EMAIL = os.getenv("DEFAULT_FROM_EMAIL", "noreply@adventureworks-analytics.local")

# Django-сообщение уровня error → Bootstrap-класс alert-danger
MESSAGE_TAGS = {message_constants.ERROR: "danger"}

# --- Контакты сайта: меняются в одном месте ---------------------------------------
SITE_ADDRESS = "г. Бишкек, ул. Айни, 209"
SITE_CONTACTS = {
    "email": "pandawow0700148815@gmail.com",
    "phone": "+996 501 22 72 24",
    "phone_href": "+996501227224",
    "address": SITE_ADDRESS,
    "map_embed_url": f"https://www.google.com/maps?q={quote_plus('Бишкек, улица Айни 209')}&output=embed",
    "map_link": f"https://www.google.com/maps/search/?api=1&query={quote_plus('Бишкек, улица Айни 209')}",
}

# --- Power BI (резервные ссылки, если в базе заглушка) -----------------------------
POWERBI_SALES_URL = os.getenv("POWERBI_SALES_URL", "")
POWERBI_MAP_URL = os.getenv("POWERBI_MAP_URL", "")

# --- Content Security Policy: разрешаем CDN, Google Fonts, Power BI и карту --------
SECURE_CSP = {
    "default-src": [CSP.SELF],
    "script-src": [CSP.SELF, "https://cdn.jsdelivr.net"],
    "style-src": [CSP.SELF, CSP.UNSAFE_INLINE, "https://cdn.jsdelivr.net", "https://fonts.googleapis.com"],
    "font-src": [CSP.SELF, "https://cdn.jsdelivr.net", "https://fonts.gstatic.com"],
    "img-src": [CSP.SELF, "data:"],
    # Соединения: свой сайт + source maps Bootstrap (их запрашивает DevTools)
    "connect-src": [CSP.SELF, "https://cdn.jsdelivr.net"],
    # Встраиваемые iframe: отчёты Power BI и Google-карта на странице контактов
    "frame-src": ["https://app.powerbi.com", "https://www.google.com", "https://maps.google.com"],
    "object-src": [CSP.NONE],
    "base-uri": [CSP.SELF],
    "form-action": [CSP.SELF],
    "frame-ancestors": [CSP.SELF],
}

# --- Безопасность в продакшене -------------------------------------------------------
if not DEBUG and not TESTING:
    SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
    SECURE_SSL_REDIRECT = env_bool("SECURE_SSL_REDIRECT", True)
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_HSTS_SECONDS = int(os.getenv("SECURE_HSTS_SECONDS", "3600"))
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True

# --- Логи в stdout (видны в логах Render) ---------------------------------------------
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "simple": {"format": "[{asctime}] {levelname} {name}: {message}", "style": "{"},
    },
    "handlers": {
        "console": {"class": "logging.StreamHandler", "stream": "ext://sys.stdout", "formatter": "simple"},
    },
    "root": {"handlers": ["console"], "level": "INFO"},
    "loggers": {
        "django": {"handlers": ["console"], "level": os.getenv("DJANGO_LOG_LEVEL", "INFO"), "propagate": False},
    },
}

