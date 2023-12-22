from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseForbidden, HttpResponse, JsonResponse
from django.shortcuts import redirect, render, get_object_or_404
from django.urls import reverse_lazy
from guardian.shortcuts import assign_perm, get_perms
from django.views import View
from django.views.generic import CreateView
from django.template.loader import render_to_string
from home.models import SiteInfo

from misar_web.settings import LOGIN_URL

from .forms import FileShareForm, FileUploadForm, MemberRegistrationForm
from guardian.shortcuts import get_objects_for_user
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
    member_files = MemberFile.objects.filter(owner=request.user).order_by("id")
    shared_files = get_objects_for_user(
        request.user, "view_memberfile", klass=MemberFile
    ).exclude(owner=request.user)
    siteinfo = SiteInfo.objects.get(id=1)
    form = FileUploadForm(request.POST or None, request.FILES or None)
    if form.is_valid():
        form.save(owner=request.user)
        if request.headers.get("HX-Request"):
            table_html = render_to_string(
                "members/personal-table.html",
                {"memberfiles": member_files, "sharedfiles": shared_files},
                request,
            )
            return HttpResponse(table_html)
        else:
            return redirect("files")
    context = {
        "form": form,
        "memberfiles": member_files,
        "sharedfiles": shared_files,
        "siteinfo": siteinfo,
    }
    return render(request, "members/files.html", context)


@login_required(redirect_field_name=LOGIN_URL, login_url=LOGIN_URL)
def delete_file(request, file_id):
    file = MemberFile.objects.get(pk=file_id)
    if request.user == file.owner or request.user.has_perm(
        "members.delete_memberfile", file
    ):
        file.delete()
        return redirect("files")
    return HttpResponseForbidden("You do not have permission to delete this file.")


@login_required(redirect_field_name=LOGIN_URL, login_url=LOGIN_URL)
def download_file(request, file_id):
    file = get_object_or_404(MemberFile, pk=file_id)
    if not (
        request.user == file.owner
        or request.user.has_perm("members.view_memberfile", file)
    ):
        return HttpResponseForbidden(
            "You do not have permission to download this file."
        )

    response = HttpResponse(file.file, content_type="application/force-download")
    response["Content-Disposition"] = f"attachment; filename={file.file_name}"
    return response


# @login_required(redirect_field_name=LOGIN_URL, login_url=LOGIN_URL)
# def file_upload(request):
#     siteinfo = SiteInfo.objects.get(id=1)
#     form = FileUploadForm(request.POST or None, request.FILES or None)
#     if form.is_valid():
#         form.save(owner=request.user)
#         return redirect("files")
#     context = {"form": form, "siteinfo": siteinfo}
#     return render(request, "members/upload.html", context)


class ShareFileView(LoginRequiredMixin, View):
    login_url = LOGIN_URL
    redirect_field_name = "redirect_to"

    def get(self, request, file_id=None):
        siteinfo = SiteInfo.objects.get(id=1)
        file_instance = None
        if file_id is not None:
            try:
                file_instance = MemberFile.objects.get(id=file_id)
            except MemberFile.DoesNotExist:
                return HttpResponseForbidden("File does not exist.")
        form = FileShareForm(initial={"file": file_instance}, user=request.user)
        context = {"form": form, "siteinfo": siteinfo}
        return render(request, "members/share_file.html", context)

    def post(self, request):
        siteinfo = SiteInfo.objects.get(id=1)
        form = FileShareForm(request.POST or None, user=request.user)
        if form.is_valid():
            file = form.cleaned_data["file"]
            recipients = form.cleaned_data["recipient"]
            permissions = form.cleaned_data["permissions"]

            if "share_memberfile" not in get_perms(request.user, file):
                return HttpResponseForbidden(
                    "You do not have permission to share this file."
                )
            for recipient in recipients:
                for permission in permissions:
                    assign_perm(permission, recipient, file)

            return redirect("files")

        context = {"form": form, "siteinfo": siteinfo}
        return render(request, "members/share_file.html", context)

