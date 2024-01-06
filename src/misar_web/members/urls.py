"""Defines URL patterns for members"""

from django.urls import path

from . import views
from .views import (
    ShareFileView,
    CustomLoginView,
    CustomLogoutView,
    CustomPasswordResetView,
    CustomPasswordResetDoneView,
    CustomPasswordResetConfirmView,
    CustomPasswordResetCompleteView,
)

urlpatterns = [
    path("register/", views.MemberRegisterView.as_view(), name="register"),
    path(
        "member_home/",
        views.member_home,
        name="member_home",
    ),
    path(
        "files/",
        views.files,
        name="files",
    ),
    path("login/", CustomLoginView.as_view(), name="login"),
    path("logout/", CustomLogoutView.as_view(), name="logout"),
    path("password_reset/", CustomPasswordResetView.as_view(), name="password_reset"),
    path(
        "password_reset/done/",
        CustomPasswordResetDoneView.as_view(),
        name="password_reset_done",
    ),
    path(
        "reset/<uidb64>/<token>/",
        CustomPasswordResetConfirmView.as_view(),
        name="password_reset_confirm",
    ),
    path(
        "reset/done/",
        CustomPasswordResetCompleteView.as_view(),
        name="password_reset_complete",
    ),
    path("delete_file/<int:file_id>/", views.delete_file, name="delete_file"),
    path("share/<int:file_id>/", ShareFileView.as_view(), name="share"),
    path("download/<int:file_id>/", views.download_file, name="download"),
    path(
        "events/",
        views.team_calendar,
        name="team_calendar",
    ),
    path("events/all/", views.all_events, name="all_events"),
    path("events/add_location/", views.create_location, name="add_location"),
]

