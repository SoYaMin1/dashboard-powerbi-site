from django.contrib import admin
from django.contrib import admin

from .models import Dashboard


@admin.register(Dashboard)
class DashboardAdmin(admin.ModelAdmin):
    list_display = ("title", "slug", "order", "is_active", "requires_login", "connected")
    list_display_links = ("title",)
    list_editable = ("order", "is_active")
    list_filter = ("is_active", "requires_login")
    search_fields = ("title", "slug", "description")
    prepopulated_fields = {"slug": ("title",)}
    fieldsets = (
        (None, {"fields": ("title", "slug", "description", "icon")}),
        ("Power BI", {
            "fields": ("embed_url", "aspect_ratio"),
            "description": "Power BI Service → открыть отчёт → File → Embed report → "
                           "Publish to web → скопировать ссылку и вставить сюда.",
        }),
        ("Публикация", {"fields": ("order", "is_active", "requires_login")}),
    )

    @admin.display(boolean=True, description="Отчёт подключён")
    def connected(self, obj):
        return obj.is_connected