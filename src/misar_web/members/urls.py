"""Defines URL patterns for members"""

from django.urls import path


from . import views

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
    path("upload/", views.file_upload, name="upload"),
]

