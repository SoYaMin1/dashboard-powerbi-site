from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.test import TestCase, override_settings
from django.urls import reverse

from .models import Dashboard

User = get_user_model()
PASSWORD = "Str0ng-Pass-2026!"
REPORT_URL = "https://app.powerbi.com/view?r=TESTREPORT123"


# Отключаем резервные ссылки из .env, чтобы тесты не зависели от локальных настроек
@override_settings(POWERBI_SALES_URL="", POWERBI_MAP_URL="")
class DashboardViewTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user("viewer", "viewer@example.com", PASSWORD)

    def detail_url(self, slug="sales"):
        return reverse("dashboards:detail", kwargs={"slug": slug})

    def test_data_migration_created_dashboards(self):
        self.assertEqual(
            set(Dashboard.objects.values_list("slug", flat=True)), {"sales", "sales-map"}
        )

    def test_anonymous_user_redirected_to_login_with_next(self):
        url = self.detail_url()
        response = self.client.get(url)
        self.assertRedirects(response, f"{reverse('accounts:login')}?next={url}")

    def test_placeholder_shows_not_connected_message(self):
        self.client.force_login(self.user)
        response = self.client.get(self.detail_url())
        self.assertContains(response, "Отчёт ещё не подключён")
        self.assertNotContains(response, "<iframe")

    def test_empty_embed_url_shows_not_connected_message(self):
        Dashboard.objects.filter(slug="sales").update(embed_url="")
        self.client.force_login(self.user)
        response = self.client.get(self.detail_url())
        self.assertContains(response, "Отчёт ещё не подключён")

    def test_connected_dashboard_renders_iframe(self):
        Dashboard.objects.filter(slug="sales").update(embed_url=REPORT_URL)
        self.client.force_login(self.user)
        response = self.client.get(self.detail_url())
        self.assertContains(response, f'src="{REPORT_URL}"')
        self.assertContains(response, 'title="Отчёт Power BI: Дашборд продаж"')
        self.assertContains(response, "--pbi-ratio: 56.25")

    @override_settings(POWERBI_MAP_URL=REPORT_URL)
    def test_env_fallback_used_when_placeholder(self):
        self.client.force_login(self.user)
        response = self.client.get(self.detail_url("sales-map"))
        self.assertContains(response, f'src="{REPORT_URL}"')
        self.assertContains(response, "pbi-wrapper--map")

    def test_public_dashboard_opens_without_login(self):
        Dashboard.objects.filter(slug="sales").update(requires_login=False)
        self.assertEqual(self.client.get(self.detail_url()).status_code, 200)

    def test_inactive_dashboard_returns_404(self):
        Dashboard.objects.filter(slug="sales").update(is_active=False)
        self.client.force_login(self.user)
        self.assertEqual(self.client.get(self.detail_url()).status_code, 404)

    def test_list_page_shows_dashboards(self):
        response = self.client.get(reverse("dashboards:list"))
        self.assertContains(response, "Дашборд продаж")
        self.assertContains(response, "Карта продаж по городам")


class DashboardModelTests(TestCase):
    def test_clean_extracts_src_from_iframe_code(self):
        dashboard = Dashboard(
            title="Тест", slug="test",
            embed_url=f'<iframe title="x" width="600" src="{REPORT_URL}" frameborder="0"></iframe>',
        )
        dashboard.clean()
        self.assertEqual(dashboard.embed_url, REPORT_URL)

    def test_clean_rejects_non_powerbi_url(self):
        dashboard = Dashboard(title="Тест", slug="test", embed_url="https://example.com/report")
        with self.assertRaises(ValidationError):
            dashboard.clean()

    def test_ratio_percent_uses_dot(self):
        self.assertEqual(Dashboard(aspect_ratio="16:9").ratio_percent, "56.25")
        self.assertEqual(Dashboard(aspect_ratio="16:10").ratio_percent, "62.5")