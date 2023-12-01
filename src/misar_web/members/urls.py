"""Defines URL patterns for members"""

from django.urls import path
from . import views
from .views import MemberRegisterView

urlpatterns = [
    path("register/", MemberRegisterView.as_view(), name="register"),
    path("member_home/", views.member_landing, name="member_home"),
    path("files/", views.file_list, name="member_files"),
    path("upload_file/", views.file_upload, name="upload_file"),
]

