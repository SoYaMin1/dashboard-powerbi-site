from django.db import migrations

PLACEHOLDER_URL = "https://app.powerbi.com/view?r=PLACEHOLDER"

DASHBOARDS = [
    {
        "slug": "sales",
        "title": "Дашборд продаж",
        "description": (
            "Основной отчёт по продажам AdventureWorks: несколько страниц с интерактивными "
            "графиками, слайсерами и фильтрами. Переключайте страницы с помощью навигации "
            "внизу отчёта."
        ),
        "icon": "bi-bar-chart-line",
        "order": 1,
    },
    {
        "slug": "sales-map",
        "title": "Карта продаж по городам",
        "description": (
            "Карта мира с городами, где продажи компании наиболее высоки. "
            "Наведите курсор на город, чтобы увидеть подробности."
        ),
        "icon": "bi-globe-americas",
        "order": 2,
    },
]


def create_dashboards(apps, schema_editor):
    Dashboard = apps.get_model("dashboards", "Dashboard")
    for data in DASHBOARDS:
        defaults = {key: value for key, value in data.items() if key != "slug"}
        defaults.update({
            "embed_url": PLACEHOLDER_URL,
            "aspect_ratio": "16:9",
            "is_active": True,
            "requires_login": True,
        })
        Dashboard.objects.get_or_create(slug=data["slug"], defaults=defaults)


def remove_dashboards(apps, schema_editor):
    Dashboard = apps.get_model("dashboards", "Dashboard")
    Dashboard.objects.filter(slug__in=[d["slug"] for d in DASHBOARDS]).delete()


class Migration(migrations.Migration):

    dependencies = [
        ("dashboards", "0001_initial"),
    ]

    operations = [
        migrations.RunPython(create_dashboards, remove_dashboards),
    ]