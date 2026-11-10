from django import forms

from .models import ContactMessage


class BootstrapFormMixin:
    """Добавляет полям Bootstrap-классы, а полям с ошибками — класс is-invalid."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            widget = field.widget
            if isinstance(widget, forms.CheckboxInput):
                css_class = "form-check-input"
            elif isinstance(widget, forms.Select):
                css_class = "form-select"
            elif isinstance(widget, forms.FileInput):
                css_class = "form-control"
            else:
                css_class = "form-control"
            widget.attrs["class"] = f"{widget.attrs.get('class', '')} {css_class}".strip()

    def full_clean(self):
        super().full_clean()
        for name in self.errors:
            if name in self.fields:
                widget = self.fields[name].widget
                widget.attrs["class"] = f"{widget.attrs.get('class', '')} is-invalid".strip()


class ContactForm(BootstrapFormMixin, forms.ModelForm):
    class Meta:
        model = ContactMessage
        fields = ["name", "email", "subject", "message"]
        widgets = {
            "name": forms.TextInput(attrs={"placeholder": "Как к вам обращаться", "autocomplete": "name"}),
            "email": forms.EmailInput(attrs={"placeholder": "name@example.com", "autocomplete": "email"}),
            "subject": forms.TextInput(attrs={"placeholder": "Тема сообщения"}),
            "message": forms.Textarea(attrs={"rows": 5, "placeholder": "Ваш вопрос или предложение"}),
        }
        error_messages = {
            "name": {"required": "Укажите ваше имя."},
            "email": {"required": "Укажите email.", "invalid": "Введите корректный email."},
            "subject": {"required": "Укажите тему сообщения."},
            "message": {"required": "Напишите сообщение."},
        }

    def clean_name(self):
        name = self.cleaned_data["name"].strip()
        if len(name) < 2:
            raise forms.ValidationError("Имя должно содержать минимум 2 символа.")
        return name

    def clean_subject(self):
        subject = self.cleaned_data["subject"].strip()
        if len(subject) < 3:
            raise forms.ValidationError("Тема должна содержать минимум 3 символа.")
        return subject

    def clean_message(self):
        message = self.cleaned_data["message"].strip()
        if len(message) < 10:
            raise forms.ValidationError("Сообщение должно содержать минимум 10 символов.")
        return message