from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import (
    AuthenticationForm,
    PasswordChangeForm,
    PasswordResetForm,
    SetPasswordForm,
    UserCreationForm,
    UsernameField,
)

from core.forms import BootstrapFormMixin

from .models import Profile

User = get_user_model()
MAX_AVATAR_SIZE_MB = 2


class RegisterForm(BootstrapFormMixin, UserCreationForm):
    email = forms.EmailField(
        label="Email",
        widget=forms.EmailInput(attrs={"autocomplete": "email", "placeholder": "name@example.com"}),
        error_messages={"required": "Укажите email.", "invalid": "Введите корректный email."},
    )
    first_name = forms.CharField(
        label="Имя", max_length=150,
        widget=forms.TextInput(attrs={"autocomplete": "given-name"}),
        error_messages={"required": "Укажите имя."},
    )
    last_name = forms.CharField(
        label="Фамилия", max_length=150,
        widget=forms.TextInput(attrs={"autocomplete": "family-name"}),
        error_messages={"required": "Укажите фамилию."},
    )

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ("username", "email", "first_name", "last_name")

    def clean_username(self):
        username = super().clean_username()
        if "@" in username:
            raise forms.ValidationError("Имя пользователя не должно содержать символ @.")
        return username

    def clean_email(self):
        email = self.cleaned_data["email"].strip().lower()
        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError("Пользователь с таким email уже зарегистрирован.")
        return email


class LoginForm(BootstrapFormMixin, AuthenticationForm):
    username = UsernameField(
        label="Имя пользователя или email",
        widget=forms.TextInput(attrs={"autofocus": True, "autocomplete": "username"}),
    )
    remember_me = forms.BooleanField(label="Запомнить меня", required=False, initial=True)

    error_messages = {
        **AuthenticationForm.error_messages,
        "invalid_login": "Неверное имя пользователя/email или пароль. "
                         "Обратите внимание: пароль чувствителен к регистру.",
    }


class UserUpdateForm(BootstrapFormMixin, forms.ModelForm):
    class Meta:
        model = User
        fields = ("first_name", "last_name", "email")
        labels = {"first_name": "Имя", "last_name": "Фамилия", "email": "Email"}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["email"].required = True
        self.fields["first_name"].required = True

    def clean_email(self):
        email = self.cleaned_data["email"].strip().lower()
        if User.objects.filter(email__iexact=email).exclude(pk=self.instance.pk).exists():
            raise forms.ValidationError("Этот email уже используется другим пользователем.")
        return email


class ProfileForm(BootstrapFormMixin, forms.ModelForm):
    class Meta:
        model = Profile
        fields = ("position", "organization", "avatar")
        widgets = {
            "position": forms.TextInput(attrs={"placeholder": "Например, аналитик данных"}),
            "organization": forms.TextInput(attrs={"placeholder": "Например, университет или компания"}),
            "avatar": forms.ClearableFileInput(attrs={"accept": "image/*"}),
        }
        help_texts = {"avatar": f"Необязательно. JPG или PNG, до {MAX_AVATAR_SIZE_MB} МБ."}

    def clean_avatar(self):
        avatar = self.cleaned_data.get("avatar")
        if avatar and hasattr(avatar, "size") and avatar.size > MAX_AVATAR_SIZE_MB * 1024 * 1024:
            raise forms.ValidationError(f"Размер файла не должен превышать {MAX_AVATAR_SIZE_MB} МБ.")
        return avatar


class StyledPasswordChangeForm(BootstrapFormMixin, PasswordChangeForm):
    pass


class StyledPasswordResetForm(BootstrapFormMixin, PasswordResetForm):
    pass


class StyledSetPasswordForm(BootstrapFormMixin, SetPasswordForm):
    pass