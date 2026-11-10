from django.contrib import admin
from django.contrib import admin

from .models import ContactMessage


@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ("subject", "name", "email", "created_at", "is_read")
    list_filter = ("is_read", "created_at")
    list_editable = ("is_read",)
    search_fields = ("name", "email", "subject", "message")
    readonly_fields = ("created_at",)
    date_hierarchy = "created_at"
    actions = ("mark_as_read", "mark_as_unread")

    @admin.action(description="Отметить как прочитанные")
    def mark_as_read(self, request, queryset):
        updated = queryset.update(is_read=True)
        self.message_user(request, f"Отмечено как прочитанные: {updated}")

    @admin.action(description="Отметить как непрочитанные")
    def mark_as_unread(self, request, queryset):
        updated = queryset.update(is_read=False)
        self.message_user(request, f"Отмечено как непрочитанные: {updated}")