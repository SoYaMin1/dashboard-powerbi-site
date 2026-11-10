from django.contrib.auth import get_user_model
from django.core import mail
from django.test import TestCase
from django.urls import reverse

from .models import Profile

User = get_user_model()
PASSWORD = "Str0ng-Pass-2026!"


class RegistrationTests(TestCase):
    url = reverse("accounts:register")

    def form_data(self, **overrides):
        data = {
            "username": "ivan",
            "email": "Ivan@Example.com",
            "first_name": "Иван",
            "last_name": "Петров",
            "password1": PASSWORD,
            "password2": PASSWORD,
        }
        data.update(overrides)
        return data

    def test_register_creates_user_with_profile_and_logs_in(self):
        response = self.client.post(self.url, self.form_data())
        self.assertRedirects(response, reverse("dashboards:detail", kwargs={"slug": "sales"}))
        user = User.objects.get(username="ivan")
        self.assertEqual(user.email, "ivan@example.com")
        self.assertTrue(Profile.objects.filter(user=user).exists())
        self.assertEqual(int(self.client.session["_auth_user_id"]), user.pk)

    def test_register_rejects_duplicate_email(self):
        User.objects.create_user("first", "taken@example.com", PASSWORD)
        response = self.client.post(self.url, self.form_data(email="TAKEN@example.com"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "уже зарегистрирован")
        self.assertEqual(User.objects.count(), 1)

    def test_register_rejects_password_mismatch(self):
        response = self.client.post(self.url, self.form_data(password2="Other-Pass-2026!"))
        self.assertEqual(response.status_code, 200)
        self.assertFalse(User.objects.filter(username="ivan").exists())


class LoginLogoutTests(TestCase):
    login_url = reverse("accounts:login")
    logout_url = reverse("accounts:logout")

    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user("anna", "anna@example.com", PASSWORD, first_name="Анна")

    def test_login_by_username_with_remember_me(self):
        response = self.client.post(self.login_url, {
            "username": "anna", "password": PASSWORD, "remember_me": "on",
        })
        self.assertRedirects(response, reverse("dashboards:list"))
        self.assertFalse(self.client.session.get_expire_at_browser_close())

    def test_login_by_email_without_remember_me(self):
        response = self.client.post(self.login_url, {"username": "ANNA@example.com", "password": PASSWORD})
        self.assertRedirects(response, reverse("dashboards:list"))
        self.assertTrue(self.client.session.get_expire_at_browser_close())

    def test_login_redirects_to_next(self):
        next_url = reverse("dashboards:detail", kwargs={"slug": "sales-map"})
        response = self.client.post(self.login_url, {
            "username": "anna", "password": PASSWORD, "next": next_url,
        })
        self.assertRedirects(response, next_url)

    def test_wrong_password_shows_error(self):
        response = self.client.post(self.login_url, {"username": "anna", "password": "wrong"})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Неверное имя пользователя")
        self.assertNotIn("_auth_user_id", self.client.session)

    def test_logout_requires_post_and_logs_out(self):
        self.client.force_login(self.user)
        self.assertEqual(self.client.get(self.logout_url).status_code, 405)
        response = self.client.post(self.logout_url)
        self.assertRedirects(response, reverse("core:home"))
        self.assertNotIn("_auth_user_id", self.client.session)


class ProfileAndPasswordTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user("anna", "anna@example.com", PASSWORD, first_name="Анна")

    def test_profile_requires_login(self):
        url = reverse("accounts:profile")
        response = self.client.get(url)
        self.assertRedirects(response, f"{reverse('accounts:login')}?next={url}")

    def test_profile_update(self):
        self.client.force_login(self.user)
        response = self.client.post(reverse("accounts:profile"), {
            "first_name": "Анна",
            "last_name": "Смирнова",
            "email": "anna@example.com",
            "position": "Аналитик данных",
            "organization": "Университет",
        })
        self.assertRedirects(response, reverse("accounts:profile"))
        self.user.refresh_from_db()
        self.assertEqual(self.user.last_name, "Смирнова")
        self.assertEqual(self.user.profile.position, "Аналитик данных")

    def test_password_reset_sends_email(self):
        response = self.client.post(reverse("accounts:password_reset"), {"email": "anna@example.com"})
        self.assertRedirects(response, reverse("accounts:password_reset_done"))
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn("/accounts/reset/", mail.outbox[0].body)

    def test_auth_pages_are_noindex(self):
        response = self.client.get(reverse("accounts:login"))
        self.assertContains(response, 'content="noindex, nofollow"')