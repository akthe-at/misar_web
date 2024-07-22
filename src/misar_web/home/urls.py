from django.urls import path
from django.views.generic import TemplateView
from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path(
        "robots.txt",
        TemplateView.as_view(template_name="robots.txt", content_type="text/plain"),
    ),
    path("<int:spec_id>/", views.icon_modal, name="icon_modal"),
    path("donate", views.donate, name="donate"),
    path("contact", views.contact, name="contact"),
    path("about", views.about, name="about"),
]
