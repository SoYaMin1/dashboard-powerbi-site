from django.shortcuts import render
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import get_user_model, login
from django.contrib.auth import views as auth_views
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.shortcuts import redirect
from django.urls import reverse, reverse_lazy
from django.utils.http import url_has_allowed_host_and_scheme
from django.views.generic import CreateView, TemplateView

from .forms import (
    LoginForm,
    ProfileForm,
    RegisterForm,
    StyledPasswordChangeForm,
    StyledPasswordResetForm,
    StyledSetPasswordForm,
    UserUpdateForm,
)
from .models import Profile

User = get_user_model()


def _safe_next(request):
    """Возвращает параметр next, только если он ведёт на наш сайт."""
    next_url = request.POST.get("next") or request.GET.get("next")
    if next_url and url_has_allowed_host_and_scheme(
        next_url, allowed_hosts={request.get_host()}, require_https=request.is_secure()
    ):
        return next_url
    return ""


class RegisterView(CreateView):
    form_class = RegisterForm
    template_name = "accounts/register.html"
    extra_context = {
        "page_title": "Регистрация",
        "page_description": "Создайте аккаунт, чтобы получить доступ к дашбордам Power BI.",
    }

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect(settings.LOGIN_REDIRECT_URL)
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["next"] = _safe_next(self.request)
        return context

    def form_valid(self, form):
        user = form.save()
        login(self.request, user, backend="accounts.backends.EmailOrUsernameBackend")
        messages.success(self.request, f"Добро пожаловать, {user.first_name}! Регистрация прошла успешно.")
        return redirect(_safe_next(self.request) or reverse("dashboards:detail", kwargs={"slug": "sales"}))


class UserLoginView(auth_views.LoginView):
    form_class = LoginForm
    template_name = "registration/login.html"
    redirect_authenticated_user = True
    extra_context = {
        "page_title": "Вход",
        "page_description": "Вход в AdventureWorks Sales Analytics.",
    }

    def form_valid(self, form):
        response = super().form_valid(form)
        if not form.cleaned_data.get("remember_me"):
            # Сессия закончится при закрытии браузера
            self.request.session.set_expiry(0)
        user = form.get_user()
        messages.success(self.request, f"Здравствуйте, {user.first_name or user.username}!")
        return response


class UserLogoutView(auth_views.LogoutView):
    """Django 5+: выход только через POST."""

    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        messages.info(request, "Вы вышли из аккаунта.")
        return response


class ProfileView(LoginRequiredMixin, TemplateView):
    template_name = "accounts/profile.html"
    extra_context = {"page_title": "Профиль"}

    def _profile(self):
        profile, _ = Profile.objects.get_or_create(user=self.request.user)
        return profile

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.setdefault("user_form", UserUpdateForm(instance=self.request.user))
        context.setdefault("profile_form", ProfileForm(instance=self._profile()))
        return context

    def post(self, request, *args, **kwargs):
        # Отдельный экземпляр, чтобы невалидные данные не попали в request.user (например, в navbar)
        user = User.objects.get(pk=request.user.pk)
        user_form = UserUpdateForm(request.POST, instance=user)
        profile_form = ProfileForm(request.POST, request.FILES, instance=self._profile())

        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, "Профиль обновлён.")
            return redirect("accounts:profile")

        messages.error(request, "Проверьте правильность заполнения полей.")
        return self.render_to_response(
            self.get_context_data(user_form=user_form, profile_form=profile_form)
        )


class UserPasswordChangeView(SuccessMessageMixin, auth_views.PasswordChangeView):
    form_class = StyledPasswordChangeForm
    template_name = "registration/password_change_form.html"
    success_url = reverse_lazy("accounts:profile")
    success_message = "Пароль успешно изменён."
    extra_context = {"page_title": "Смена пароля"}


class UserPasswordResetView(auth_views.PasswordResetView):
    form_class = StyledPasswordResetForm
    template_name = "registration/password_reset_form.html"
    email_template_name = "registration/password_reset_email.html"
    subject_template_name = "registration/password_reset_subject.txt"
    success_url = reverse_lazy("accounts:password_reset_done")
    extra_context = {"page_title": "Восстановление пароля"}


class UserPasswordResetDoneView(auth_views.PasswordResetDoneView):
    template_name = "registration/password_reset_done.html"
    extra_context = {"page_title": "Письмо отправлено"}


class UserPasswordResetConfirmView(auth_views.PasswordResetConfirmView):
    form_class = StyledSetPasswordForm
    template_name = "registration/password_reset_confirm.html"
    success_url = reverse_lazy("accounts:password_reset_complete")
    extra_context = {"page_title": "Новый пароль"}


class UserPasswordResetCompleteView(auth_views.PasswordResetCompleteView):
    template_name = "registration/password_reset_complete.html"
    extra_context = {"page_title": "Пароль изменён"}