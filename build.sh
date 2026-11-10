#!/usr/bin/env bash
# Сборка на Render: установка зависимостей, статика, миграции, суперпользователь
set -o errexit

pip install -r requirements.txt
python manage.py collectstatic --no-input
python manage.py migrate

# Создать суперпользователя из переменных DJANGO_SUPERUSER_*, если его ещё нет
python manage.py createsuperuser --no-input || true