from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .models import Profile

User = get_user_model()


class ProfileInline(admin.StackedInline):
    model = Profile
    can_delete = False
    verbose_name_plural = "Профиль"
    fields = ("position", "organization", "avatar")


admin.site.unregister(User)


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    inlines = [ProfileInline]
    list_display = ("username", "email", "first_name", "last_name", "is_staff", "date_joined")

    def get_inline_instances(self, request, obj=None):
        # При создании пользователя профиль создаёт сигнал, поэтому inline показываем только при редактировании
        if obj is None:
            return []
        return super().get_inline_instances(request, obj)