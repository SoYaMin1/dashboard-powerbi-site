from django.urls import path

from . import views

app_name = "dashboards"

urlpatterns = [
    path("", views.DashboardListView.as_view(), name="list"),
    path("<slug:slug>/", views.DashboardDetailView.as_view(), name="detail"),
]