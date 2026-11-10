from django.db import models

import re
from urllib.parse import urlparse

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.urls import reverse

PLACEHOLDER_URL = "https://app.powerbi.com/view?r=PLACEHOLDER"

# Если в базе заглушка, берём ссылку из переменной окружения (settings.POWERBI_*)
ENV_FALLBACKS = {
    "sales": "POWERBI_SALES_URL",
    "sales-map": "POWERBI_MAP_URL",
}

IFRAME_SRC_RE = re.compile(r'src\s*=\s*["\']([^"\']+)["\']', re.IGNORECASE)


def is_placeholder(url):
    """Пустая ссылка или заглушка считаются «отчёт не подключён»."""
    url = (url or "").strip()
    return not url or "PLACEHOLDER" in url.upper()


class Dashboard(models.Model):
    class AspectRatio(models.TextChoices):
        WIDE = "16:9", "16:9"
        WIDE_10 = "16:10", "16:10"

    RATIO_PERCENT = {"16:9": "56.25", "16:10": "62.5"}

    title = models.CharField("Название", max_length=200)
    slug = models.SlugField("Адрес (slug)", max_length=100, unique=True)
    description = models.TextField("Описание", blank=True, help_text="Текст над отчётом.")
    embed_url = models.CharField(
        "Ссылка Power BI",
        max_length=2000,
        blank=True,
        default=PLACEHOLDER_URL,
        help_text="Ссылка из Power BI → File → Embed report → Publish to web "
                  "(вида https://app.powerbi.com/view?r=...). "
                  "Можно вставить и весь HTML-код iframe — ссылка извлечётся автоматически.",
    )
    icon = models.CharField(
        "Иконка", max_length=50, default="bi-bar-chart-line",
        help_text="Класс Bootstrap Icons, например bi-bar-chart-line или bi-globe-americas.",
    )
    aspect_ratio = models.CharField(
        "Пропорции", max_length=5, choices=AspectRatio.choices, default=AspectRatio.WIDE,
    )
    order = models.PositiveIntegerField("Порядок", default=0)
    is_active = models.BooleanField("Активен", default=True)
    requires_login = models.BooleanField("Только для авторизованных", default=True)

    class Meta:
        ordering = ["order", "title"]
        verbose_name = "Дашборд"
        verbose_name_plural = "Дашборды"

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse("dashboards:detail", kwargs={"slug": self.slug})

    def clean(self):
        url = (self.embed_url or "").strip()
        # Если вставили целиком <iframe ...>, достаём src
        if "<iframe" in url.lower():
            match = IFRAME_SRC_RE.search(url)
            url = match.group(1) if match else ""
        self.embed_url = url

        if url and not is_placeholder(url):
            parsed = urlparse(url)
            if parsed.scheme != "https" or not parsed.netloc.endswith("powerbi.com"):
                raise ValidationError({
                    "embed_url": "Укажите ссылку Power BI вида https://app.powerbi.com/view?r=..."
                })

    @property
    def resolved_embed_url(self):
        """Ссылка из базы, а если там заглушка — из переменной окружения."""
        if not is_placeholder(self.embed_url):
            return self.embed_url.strip()
        setting_name = ENV_FALLBACKS.get(self.slug)
        fallback = getattr(settings, setting_name, "") if setting_name else ""
        return "" if is_placeholder(fallback) else fallback.strip()

    @property
    def is_connected(self):
        return bool(self.resolved_embed_url)

    @property
    def ratio_percent(self):
        # Строка, а не float: иначе русская локаль выведет «56,25» и сломает CSS
        return self.RATIO_PERCENT.get(self.aspect_ratio, "56.25")

    @property
    def is_map(self):
        return self.slug == "sales-map"