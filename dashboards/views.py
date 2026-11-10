from django.contrib.auth.views import redirect_to_login
from django.views.generic import DetailView, ListView

from .models import Dashboard


class DashboardListView(ListView):
    model = Dashboard
    template_name = "dashboards/list.html"
    context_object_name = "dashboards"
    extra_context = {
        "page_title": "Дашборды",
        "page_description": "Все отчёты Power BI проекта AdventureWorks Sales Analytics.",
    }

    def get_queryset(self):
        return Dashboard.objects.filter(is_active=True)


class DashboardDetailView(DetailView):
    model = Dashboard
    template_name = "dashboards/detail.html"
    context_object_name = "dashboard"

    def get_queryset(self):
        return Dashboard.objects.filter(is_active=True)

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        if self.object.requires_login and not request.user.is_authenticated:
            # Перенаправление на вход с параметром ?next=/dashboards/<slug>/
            return redirect_to_login(request.get_full_path())
        context = self.get_context_data(object=self.object)
        return self.render_to_response(context)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        dashboard = self.object
        context["page_title"] = dashboard.title
        context["page_description"] = (
            dashboard.description[:155] if dashboard.description
            else f"Отчёт Power BI «{dashboard.title}» по данным AdventureWorksDW2022."
        )
        context["embed_url"] = dashboard.resolved_embed_url
        context["other_dashboards"] = Dashboard.objects.filter(is_active=True).exclude(pk=dashboard.pk)
        return context