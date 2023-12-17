from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.http import HttpResponseForbidden, HttpResponse
from django.shortcuts import redirect, render, get_object_or_404
from django.urls import reverse_lazy
from django.db import IntegrityError, transaction
from django.views import View
from django.views.generic import CreateView
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from home.models import SiteInfo

from misar_web.settings import LOGIN_URL

from .forms import FilePermissionForm, FileUploadForm, MemberRegistrationForm
from .models import FilePermission, MemberFile, Member
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
    member_files = MemberFile.objects.filter(owner=request.user).order_by("id")
    shared_files = MemberFile.objects.filter(shared_with=request.user).exclude(
        owner=request.user
    )
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
    if request.user == file.owner or request.user.has_perm("delete_memberfile", file):
        file.delete()
        return redirect("files")
    return HttpResponseForbidden("You do not have permission to delete this file.")


@login_required(redirect_field_name=LOGIN_URL, login_url=LOGIN_URL)
def download_file(request, file_id):
    file = get_object_or_404(MemberFile, pk=file_id)
    print("User: ", request.user)
    print("File: ", file)
    if not (
        request.user == file.owner or request.user.has_perm("view_memberfile", file)
    ):
        return HttpResponseForbidden(
            "You do not have permission to download this file."
        )

    response = HttpResponse(file.file, content_type="application/force-download")
    response["Content-Disposition"] = f"attachment; filename={file.file_name}"
    return response


@login_required(redirect_field_name=LOGIN_URL, login_url=LOGIN_URL)
def file_upload(request):
    siteinfo = SiteInfo.objects.get(id=1)
    form = FileUploadForm(request.POST or None, request.FILES or None)
    if form.is_valid():
        form.save(owner=request.user)
        return redirect("files")
    context = {"form": form, "siteinfo": siteinfo}
    return render(request, "members/upload.html", context)


class ShareFileView(LoginRequiredMixin, View):
    login_url = LOGIN_URL
    redirect_field_name = "redirect_to"

    def get(self, request):
        siteinfo = SiteInfo.objects.get(id=1)
        form = FilePermissionForm(
            initial={"file": request.GET.get("file")}, user=request.user
        )
        context = {"form": form, "siteinfo": siteinfo}
        return render(request, "members/share_file.html", context)

    def post(self, request):
        siteinfo = SiteInfo.objects.get(id=1)
        form = FilePermissionForm(request.POST or None, user=request.user)
        if form.is_valid():
            file = form.cleaned_data["file"]
            recipient = form.cleaned_data["recipient"]
            permissions = form.cleaned_data.get("permissions", [])
            print(form.cleaned_data)

            try:
                file_permission = FilePermission(
                    file=file, recipient=recipient, permissions=permissions
                )
                file_permission.save()
            except IntegrityError as e:
                print(e)
                messages.warning(
                    request,
                    f"{recipient} already has permissions for {file.file_name}.",
                )

            return redirect("files")
        print(form.errors)
        context = {"form": form, "siteinfo": siteinfo}
        return render(request, "members/share_file.html", context)

