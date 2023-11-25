"""Defines URL patterns for members"""

from django.urls import path
from .views import MemberRegisterView

urlpatterns = [
    path("register/", MemberRegisterView.as_view(), name="register"),
]

