from django.urls import path

from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("<int:spec_id>/", views.icon_modal, name="icon_modal"),
    path("donate", views.donate, name="donate"),
    path("contact", views.contact, name="contact"),
    path("about", views.about, name="about"),
]
