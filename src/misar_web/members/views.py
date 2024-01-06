from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.contrib.auth.views import (
    LoginView,
    LogoutView,
    PasswordResetCompleteView,
    PasswordResetConfirmView,
    PasswordResetDoneView,
    PasswordResetView,
)
from django.http import HttpRequest, HttpResponse, HttpResponseForbidden
from django.shortcuts import get_object_or_404, redirect, render
from django.template.loader import render_to_string
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import CreateView
from guardian.shortcuts import assign_perm, get_objects_for_user, get_perms
from home.models import SiteInfo
import calendar
from calendar import HTMLCalendar
from datetime import datetime
from misar_web.settings import LOGIN_URL

from .forms import (
    EventLocationForm,
    FileShareForm,
    FileUploadForm,
    MemberRegistrationForm,
)
from .models import Member, MemberFile, Event


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
def member_home(request: HttpRequest):
    siteinfo = SiteInfo.objects.get(id=1)
    context = {"siteinfo": siteinfo}
    return render(request, "members/member_landing.html", context)


@login_required(redirect_field_name=LOGIN_URL, login_url=LOGIN_URL)
def files(request: HttpRequest):
    DEFAULT_PERMS = [
        "view_memberfile",
        "change_memberfile",
        "delete_memberfile",
        "share_memberfile",
    ]
    siteinfo = SiteInfo.objects.get(id=1)
    member_files = MemberFile.objects.filter(owner=request.user).order_by("id")  # noqa
    shared_files = get_objects_for_user(
        request.user, "view_memberfile", klass=MemberFile
    ).exclude(owner=request.user)
    form = FileUploadForm(request.POST or None, request.FILES or None)
    if form.is_valid():
        file = form.save(owner=request.user)
        for permission in DEFAULT_PERMS:
            assign_perm(permission, request.user, file)

        member_files = MemberFile.objects.filter(owner=request.user).order_by("id")
        if request.headers.get("HX-Request"):
            member_table_html = render_to_string(
                "members/partials/personal-table.html",
                {"memberfiles": member_files},
                request,
            )

            return HttpResponse(member_table_html)
        else:
            return redirect("files")
    else:
        member_files = MemberFile.objects.filter(owner=request.user).order_by("id")
        share_form = FileShareForm(user=request.user)
    context = {
        "form": form,
        "memberfiles": member_files,
        "sharedfiles": shared_files,
        "siteinfo": siteinfo,
        "share_form": share_form,
    }
    return render(request, "members/files.html", context)


@login_required(redirect_field_name=LOGIN_URL, login_url=LOGIN_URL)
def delete_file(request: HttpRequest, file_id: int):
    file = MemberFile.objects.get(pk=file_id)
    if request.user == file.owner or request.user.has_perm(
        "members.delete_memberfile", file
    ):
        file.file.delete()
        file.delete()
    else:
        messages.error(request, "You do not have permission to delete this file.")

    if request.headers.get("HX-Request"):
        if "shared-files-table" in request.headers.get("HX-Target", ""):
            files = get_objects_for_user(
                request.user, "view_memberfile", klass=MemberFile
            ).exclude(owner=request.user)
            table_html = render_to_string(
                "members/partials/shared-table.html",
                {"sharedfiles": files},
                request,
            )
        else:
            files = MemberFile.objects.filter(owner=request.user).order_by("id")
            table_html = render_to_string(
                "members/partials/personal-table.html",
                {"memberfiles": files},
                request,
            )
        return HttpResponse(table_html)


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

    def post(self, request, file_id=None):
        siteinfo = SiteInfo.objects.get(id=1)
        form = FileShareForm(request.POST or None, user=request.user)
        if form.is_valid():
            file = form.cleaned_data["file"]
            recipients = form.cleaned_data["recipient"]
            assign_to_all = form.cleaned_data["assign_to_all"]
            permissions = form.cleaned_data["permissions"]

            if "share_memberfile" not in get_perms(request.user, file):
                return HttpResponseForbidden(
                    "You do not have permission to share this file."
                )
            if assign_to_all:
                all_users = Member.objects.all().exclude(is_superuser=True)
                for user in all_users:
                    for permission in permissions:
                        assign_perm(permission, user, file)
            else:
                for recipient in recipients:
                    for permission in permissions:
                        assign_perm(permission, recipient, file)

            return redirect("files")

        context = {"form": form, "siteinfo": siteinfo}
        return render(request, "members/share_file.html", context)


@login_required(redirect_field_name=LOGIN_URL, login_url=LOGIN_URL)
def team_calendar(request: HttpRequest):
    now = datetime.now()
    year = now.year
    month = now.strftime("%B")

    month_number = list(calendar.month_name).index(month)
    cal = HTMLCalendar().formatmonth(int(year), month_number)

    siteinfo = SiteInfo.objects.get(id=1)
    context = {
        "siteinfo": siteinfo,
        "year": year,
        "month": month,
        "month_number": month_number,
        "cal": cal,
    }
    return render(request, "members/events/calendar.html", context)


def all_events(request: HttpRequest):
    siteinfo = SiteInfo.objects.get(id=1)
    events = Event.objects.all()
    context = {"siteinfo": siteinfo, "events": events}
    return render(request, "members/events/all_events.html", context)


def create_location(request: HttpRequest):
    siteinfo = SiteInfo.objects.get(id=1)
    form = EventLocationForm(request.POST or None)
    if form.is_valid():
        form.save()
        return redirect("all_events")
    context = {"siteinfo": siteinfo, "form": form}
    return render(request, "members/events/add_location.html", context)

