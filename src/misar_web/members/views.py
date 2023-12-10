from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseForbidden
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import CreateView
from home.models import SiteInfo

from misar_web.settings import LOGIN_URL

from .forms import FileSharingForm, FileUploadForm, MemberRegistrationForm
from .models import MemberFile
from django.contrib.auth.views import (
    LoginView,
    LogoutView,
    PasswordResetView,
    PasswordResetDoneView,
    PasswordResetConfirmView,
    PasswordResetCompleteView,
)


class MemberRegisterView(CreateView):
    form_class = MemberRegistrationForm
    template_name = "registration/register.html"
    success_url = reverse_lazy("login")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["siteinfo"] = SiteInfo.objects.get(id=1)
        return context


class CustomPasswordResetView(PasswordResetView):
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["siteinfo"] = SiteInfo.objects.get(id=1)
        return context


class CustomPasswordResetDoneView(PasswordResetDoneView):
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["siteinfo"] = SiteInfo.objects.get(id=1)
        return context


class CustomPasswordResetConfirmView(PasswordResetConfirmView):
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["siteinfo"] = SiteInfo.objects.get(id=1)
        return context


class CustomPasswordResetCompleteView(PasswordResetCompleteView):
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["siteinfo"] = SiteInfo.objects.get(id=1)
        return context


class CustomLoginView(LoginView):
    """Extend base LoginView to add extra data"""

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["siteinfo"] = SiteInfo.objects.get(id=1)
        return context


class CustomLogoutView(LogoutView):
    """Extend base LoginView to add extra data"""

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["siteinfo"] = SiteInfo.objects.get(id=1)
        return context


@login_required(redirect_field_name=LOGIN_URL, login_url=LOGIN_URL)
def member_home(request):
    siteinfo = SiteInfo.objects.get(id=1)
    context = {"siteinfo": siteinfo}
    return render(request, "members/member_landing.html", context)


@login_required(redirect_field_name=LOGIN_URL, login_url=LOGIN_URL)
def files(request):
    member_files = MemberFile.objects.filter(current_owner=request.user)
    shared_files = MemberFile.objects.filter(users=request.user)
    siteinfo = SiteInfo.objects.get(id=1)
    context = {
        "memberfiles": member_files,
        "sharedfiles": shared_files,
        "siteinfo": siteinfo,
    }
    return render(request, "members/files.html", context)


@login_required(redirect_field_name=LOGIN_URL, login_url=LOGIN_URL)
def delete_file(request, file_id):
    file = MemberFile.objects.get(pk=file_id)
    if request.user == file.current_owner or request.user.has_perm("delete_file", file):
        file.delete()
        return redirect("files")
    return HttpResponseForbidden("You do not have permission to delete this file.")


@login_required(redirect_field_name=LOGIN_URL, login_url=LOGIN_URL)
def file_upload(request):
    siteinfo = SiteInfo.objects.get(id=1)
    form = FileUploadForm(request.POST or None, request.FILES or None)
    if form.is_valid():
        obj = form.save(commit=False)
        if request.user.is_authenticated:
            obj.user = request.user
            obj.current_owner = request.user
            obj.save()
            return redirect("files")
        form.add_error(None, "You must be logged in to upload files.")
    context = {"form": form, "siteinfo": siteinfo}
    return render(request, "members/upload.html", context)


class ShareFileView(LoginRequiredMixin, View):
    login_url = LOGIN_URL
    redirect_field_name = "redirect_to"

    def get(self, request):
        siteinfo = SiteInfo.objects.get(id=1)
        form = FileSharingForm(user=request.user)
        context = {"form": form, "siteinfo": siteinfo}
        return render(request, "members/share_file.html", context)

    def post(self, request):
        siteinfo = SiteInfo.objects.get(id=1)
        form = FileSharingForm(request.POST or None, user=request.user)
        if form.is_valid():
            file_sharing = form.save(commit=False)
            file_sharing.save()

            permissions = form.cleaned_data["permissions"]
            for permission in permissions:
                file_sharing.permissions.add(permission)
            form.save_m2m()
            return redirect("files")

        context = {"form": form, "siteinfo": siteinfo}
        return render(request, "members/share_file.html", context)

