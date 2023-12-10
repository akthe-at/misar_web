"""Defines URL patterns for members"""

from django.urls import path

from . import views
from .views import ShareFileView

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
    path("delete_file/<int:file_id>/", views.delete_file, name="delete_file"),
    path("upload/", views.file_upload, name="upload"),
    path("share/", ShareFileView.as_view(), name="share"),
]
