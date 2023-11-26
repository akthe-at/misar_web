from django.views import generic
from django.urls import reverse_lazy

from .forms import MemberRegistrationForm


class MemberRegisterView(generic.CreateView):
    form_class = MemberRegistrationForm
    template_name = "registration/register.html"
    success_url = reverse_lazy("login")

