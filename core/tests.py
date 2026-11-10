import re
from django.test import TestCase
from django.urls import reverse

from .models import ContactMessage

PUBLIC_PAGES = ("core:home", "core:about", "core:contacts")


class PublicPagesTests(TestCase):
    def test_public_pages_open(self):
        for name in PUBLIC_PAGES:
            with self.subTest(page=name):
                self.assertEqual(self.client.get(reverse(name)).status_code, 200)

    def test_pages_have_unique_title_and_description(self):
        titles, descriptions = set(), set()
        for name in PUBLIC_PAGES:
            html = self.client.get(reverse(name)).content.decode()
            titles.add(re.search(r"<title>(.*?)</title>", html, re.S).group(1).strip())
            descriptions.add(re.search(r'<meta name="description" content="([^"]*)"', html).group(1))
            self.assertIn('property="og:title"', html)
            self.assertIn('rel="canonical"', html)
        self.assertEqual(len(titles), len(PUBLIC_PAGES))
        self.assertEqual(len(descriptions), len(PUBLIC_PAGES))

    def test_active_menu_item_is_highlighted(self):
        html = self.client.get(reverse("core:about")).content.decode()
        self.assertRegex(html, r'aria-current="page"\s+href="/about/"')

    def test_contacts_shown_in_footer(self):
        response = self.client.get(reverse("core:home"))
        self.assertContains(response, 'href="tel:+996501227224"')
        self.assertContains(response, 'href="mailto:')

    def test_custom_404_page(self):
        response = self.client.get("/no-such-page/")
        self.assertEqual(response.status_code, 404)
        self.assertTemplateUsed(response, "404.html")

    def test_csp_allows_powerbi_iframes(self):
        response = self.client.get(reverse("core:home"))
        self.assertIn("https://app.powerbi.com", response.headers["Content-Security-Policy"])


class ContactFormTests(TestCase):
    url = reverse("core:contacts")

    def test_valid_form_saves_message_and_redirects(self):
        response = self.client.post(self.url, {
            "name": "Иван",
            "email": "ivan@example.com",
            "subject": "Вопрос по проекту",
            "message": "Здравствуйте! Хочу узнать подробнее о дашбордах.",
        }, follow=True)
        self.assertRedirects(response, self.url)
        self.assertContains(response, "Спасибо, сообщение отправлено")
        message = ContactMessage.objects.get()
        self.assertEqual(message.email, "ivan@example.com")
        self.assertFalse(message.is_read)

    def test_invalid_form_shows_errors_and_saves_nothing(self):
        response = self.client.post(self.url, {
            "name": "", "email": "not-an-email", "subject": "", "message": "коротко",
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Введите корректный email.")
        self.assertContains(response, "is-invalid")
        self.assertEqual(ContactMessage.objects.count(), 0)