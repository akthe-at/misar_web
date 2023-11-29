from django.views import generic
from django.urls import reverse_lazy
from django.shortcuts import render
from django.contrib.auth.decorators import login_required

from misar_web.settings import LOGIN_URL
from .forms import MemberRegistrationForm


class MemberRegisterView(generic.CreateView):
    form_class = MemberRegistrationForm
    template_name = "registration/register.html"
    success_url = reverse_lazy("login")


@login_required(redirect_field_name=LOGIN_URL, login_url=LOGIN_URL)
def member_landing(request):
    return render(request, template_name="members/member_landing.html")

