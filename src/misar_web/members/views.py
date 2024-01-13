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
from django.http import (
    HttpRequest,
    HttpResponse,
    HttpResponseForbidden,
    HttpResponseRedirect,
)
from django.shortcuts import get_object_or_404, redirect, render
from django.template.loader import render_to_string
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import CreateView
import csv
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
    EventForm,
)
from .models import Member, MemberFile, Event, Location


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
            files = MemberFile.objects.filter(owner=request.user).order_by("id")
            return render(
                request, "members/files.html#personal-table", {"memberfiles": files}
            )
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
def delete_file(request: HttpRequest, file_id: int) -> HttpResponse | None:
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
            return render(
                request, "members/files.html#shared-files-table", {"sharedfiles": files}
            )

        else:
            files = MemberFile.objects.filter(owner=request.user).order_by("id")
        return render(
            request, "members/files.html#personal-table", {"memberfiles": files}
        )


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
    events = Event.objects.all().order_by("date")
    context = {"siteinfo": siteinfo, "events": events}
    return render(request, "members/events/all_events.html", context)


def create_event(request: HttpRequest):
    siteinfo = SiteInfo.objects.get(id=1)
    if request.method == "POST":
        form = EventForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("all_events")
    else:
        form = EventForm()
    context = {"siteinfo": siteinfo, "form": form}
    return render(request, "members/events/add_event.html", context)


def update_event(request: HttpRequest, event_id: int):
    siteinfo = SiteInfo.objects.get(id=1)
    event = Event.objects.get(pk=event_id)
    if request.method == "POST":
        form = EventForm(request.POST, instance=event)
        if form.is_valid():
            form.save()
            return redirect("all_events")
    else:
        form = EventForm(instance=event)
    context = {"siteinfo": siteinfo, "form": form}
    return render(request, "members/events/update_event.html", context)


@login_required(redirect_field_name=LOGIN_URL, login_url=LOGIN_URL)
def delete_event(request: HttpRequest, event_id: int):
    event = Event.objects.get(pk=event_id)
    event.delete()
    return redirect("all_events")


def create_location(request: HttpRequest):
    submitted = False
    siteinfo = SiteInfo.objects.get(id=1)
    if request.method == "POST":
        form = EventLocationForm(request.POST)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect("?submitted=True")
    else:
        form = EventLocationForm()
        if "submitted" in request.GET:
            submitted = True

    context = {"siteinfo": siteinfo, "form": form, "submitted": submitted}
    return render(request, "members/events/add_location.html", context)


def list_locations(request: HttpRequest):
    siteinfo = SiteInfo.objects.get(id=1)
    location_list = Location.objects.all().order_by("name")
    context = {"siteinfo": siteinfo, "location_list": location_list}
    return render(request, "members/events/locations.html", context)


def show_location(request: HttpRequest, location_id: int):
    location = Location.objects.get(pk=location_id)
    siteinfo = SiteInfo.objects.get(id=1)
    context = {"location": location, "siteinfo": siteinfo}
    return render(
        request,
        template_name="members/events/show_location.html",
        context=context,
    )


def update_location(request: HttpResponse, location_id: int):
    location = Location.objects.get(pk=location_id)
    siteinfo = SiteInfo.objects.get(id=1)
    form = EventLocationForm(request.POST or None, instance=location)

    if request.method == "POST":
        if form.is_valid():
            form.save()
            return redirect("location_list")

    return render(
        request,
        "members/events/update_location.html",
        {"location": location, "siteinfo": siteinfo, "form": form},
    )


def delete_location(request: HttpRequest, location_id: int):
    location = Location.objects.get(pk=location_id)
    location.delete()
    return redirect("location_list")


def location_csv(request: HttpRequest) -> HttpResponse:
    """A view for exporting locations as a CSV file.

    Args:
        request: HttpRequest

    Returns:
        HttpResponse: A CSV file of locations.
    """
    if request.method == "POST":
        response = HttpResponse(content_type="text/csv")
        response["Content-Disposition"] = 'attachment; filename="locations.csv"'
        writer = csv.writer(response)

        writer.writerow(
            [
                "Location Name",
                "Address",
                "City",
                "State",
                "Zip Code",
                "POC Name",
                "Phone Number",
                "Email",
                "Website",
                "Description",
                "MISAR Point of Contact",
            ]
        )
        location_ids = request.POST.getlist("location_ids")
        print(location_ids)
        print(type(location_ids))
        locations = Location.objects.filter(pk__in=location_ids).values_list(
            "name",
            "address",
            "city",
            "state",
            "zip_code",
            "point_of_contact",
            "phone_number",
            "email",
            "website",
            "description",
            "misar_poc",
        )
        for location in locations:
            writer.writerow(location)
        return response

