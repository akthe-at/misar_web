"""Defines URL patterns for members"""

from django.urls import path

from . import views
from .views import (
    CustomLoginView,
    CustomLogoutView,
    CustomPasswordResetCompleteView,
    CustomPasswordResetConfirmView,
    CustomPasswordResetDoneView,
    CustomPasswordResetView,
    ShareFileView,
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
        views.all_events,
        name="all_events",
    ),
    path("events/add_location/", views.create_location, name="add_location"),
    path("events/locations/", views.list_locations, name="location_list"),
    path("events/locations/search", views.search_locations, name="location_search"),
    path(
        "events/show_location/<location_id>/", views.show_location, name="show_location"
    ),
    path(
        "events/update_location/<location_id>/",
        views.update_location,
        name="update_location",
    ),
    path("events/update_event/<event_id>/", views.update_event, name="update_event"),
    path(
        "events/delete_location/<location_id>/",
        views.delete_location,
        name="delete_location",
    ),
    path("events/add_event/", views.create_event, name="add_event"),
    path("events/delete_event/<event_id>/", views.delete_event, name="delete_event"),
    path("events/filter_events/", views.filter_events, name="filter_events"),
    path("location_csv", views.location_csv, name="location_csv"),
]
