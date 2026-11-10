from django.contrib.messages.views import SuccessMessageMixin
from django.urls import reverse_lazy
from django.views.generic import CreateView, TemplateView

from .forms import ContactForm
from .models import ContactMessage


class HomeView(TemplateView):
    template_name = "core/home.html"
    extra_context = {
        "page_description": "Интерактивные отчёты Power BI по продажам AdventureWorks: "
                            "динамика, география, продукты и категории.",
    }


class AboutView(TemplateView):
    template_name = "core/about.html"
    extra_context = {
        "page_title": "О проекте",
        "page_description": "Цель проекта, технологии и схема работы: "
                            "AdventureWorksDW2022 → Power BI → сайт на Django.",
    }


class ContactView(SuccessMessageMixin, CreateView):
    model = ContactMessage
    form_class = ContactForm
    template_name = "core/contacts.html"
    success_url = reverse_lazy("core:contacts")
    success_message = "Спасибо, сообщение отправлено"
    extra_context = {
        "page_title": "Контакты",
        "page_description": "Свяжитесь с автором проекта AdventureWorks Sales Analytics: "
                            "email, телефон, адрес и форма обратной связи.",
    }

    def get_initial(self):
        initial = super().get_initial()
        user = self.request.user
        if user.is_authenticated:
            initial["name"] = user.get_full_name() or user.username
            initial["email"] = user.email
        return initial

