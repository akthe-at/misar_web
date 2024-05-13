import csv

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import Group
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import (
    LoginView,
    LogoutView,
    PasswordResetCompleteView,
    PasswordResetConfirmView,
    PasswordResetDoneView,
    PasswordResetView,
)
from django.core.paginator import Paginator
from django.http import (
    HttpRequest,
    HttpResponse,
    HttpResponseForbidden,
    HttpResponseRedirect,
)
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import CreateView, ListView
from guardian.shortcuts import assign_perm, get_objects_for_user, get_perms
from home.models import SiteInfo
from misar_web.settings import LOGIN_URL

from .forms import (
    EventForm,
    EventLocationForm,
    FileShareForm,
    FileUploadForm,
    MemberRegistrationForm,
)
from .models import Event, Location, Member, MemberFile


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
    def form_invalid(self, form):
        messages.error(self.request, "Incorrect username or password.")
        return super().form_invalid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["siteinfo"] = SiteInfo.objects.get(id=1)
        return context


class CustomLogoutView(LogoutView):
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


class CalendarView(LoginRequiredMixin, ListView):
    login_url = LOGIN_URL
    model = Event
    template_name = "calendar.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        d = get_date(self.request.GET.get("month", None))
        cal = Calendar(d.year, d.month)
        html_cal = cal.formatmonth(withyear=True)
        context["calendar"] = mark_safe(html_cal)
        context["prev_month"] = prev_month(d)
        context["next_month"] = next_month(d)
        return context


@login_required(redirect_field_name=LOGIN_URL, login_url=LOGIN_URL)
def all_events(request: HttpRequest):
    siteinfo = SiteInfo.objects.get(id=1)
    events = Event.objects.all().order_by("date")
    context = {"siteinfo": siteinfo, "events": events}
    return render(request, "members/events/all_events.html", context)


@login_required(redirect_field_name=LOGIN_URL, login_url=LOGIN_URL)
def create_event(request: HttpRequest):
    DEFAULT_PERMS = [
        "add_event",
        "change_event",
        "delete_event",
    ]
    siteinfo = SiteInfo.objects.get(id=1)
    form = EventForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        event_organizer = form.cleaned_data["event_organizer"]
        event_name = form.cleaned_data["event_name"]
        description = form.cleaned_data["description"]
        event_type = form.cleaned_data["event_type"]
        date = form.cleaned_data["date"]
        location = form.cleaned_data["location"]
        start_time = form.cleaned_data["start_time"]
        end_time = form.cleaned_data["end_time"]
        special_instructions = form.cleaned_data["special_instructions"]
        event, created = Event.objects.get_or_create(
            event_poster=request.user,
            event_organizer=event_organizer,
            event_name=event_name,
            description=description,
            event_type=event_type,
            date=date,
            location=location,
            start_time=start_time,
            end_time=end_time,
            special_instructions=special_instructions,
        )
        for permission in DEFAULT_PERMS:
            assign_perm(permission, request.user, event)
            assign_perm(permission, event_organizer, event)
        request.user.save()
        event_organizer.save()
        # TODO: Fix moderator permission assignments
        # moderator_group, created = Group.objects.get_or_create(name="moderator")
        # assign_perm(DEFAULT_PERMS, moderator_group, event)
        return redirect("all_events")
    context = {"siteinfo": siteinfo, "form": form}
    return render(request, "members/events/add_event.html", context)


@login_required(redirect_field_name=LOGIN_URL, login_url=LOGIN_URL)
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
    siteinfo = SiteInfo.objects.get(id=1)
    events = Event.objects.all().order_by("date")
    context = {"siteinfo": siteinfo, "events": events}
    return render(request, "members/events/all_events.html", context)


# class EventMemberDeleteView(LoginRequiredMixin, DeleteView):
#     login_url = LOGIN_URL
#     model = EventMember
#     successful_url = reverse_lazy("all_events")
#
#     def get(self, request, event_id, member_id):
#         event = get_object_or_404(Event, pk=event_id)
#         member = get_object_or_404(Member, pk=member_id)
#         event_member = get_object_or_404(EventMember, event=event, member=member)
#         event_member.delete()
#         return redirect("all_events")


@login_required(redirect_field_name=LOGIN_URL, login_url=LOGIN_URL)
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


@login_required(redirect_field_name=LOGIN_URL, login_url=LOGIN_URL)
def list_locations(request: HttpRequest):
    siteinfo = SiteInfo.objects.get(id=1)
    location_list = Location.objects.all().order_by("name")

    # PAGEINATION
    p = Paginator(location_list, 10)
    page = request.GET.get("page")
    locations = p.get_page(page)

    context = {
        "siteinfo": siteinfo,
        "locations": locations,
    }
    return render(request, "members/events/locations.html", context)


@login_required(redirect_field_name=LOGIN_URL, login_url=LOGIN_URL)
def search_locations(request: HttpRequest):
    search_text = request.POST.get("search")
    results = Location.objects.filter(name__icontains=search_text)

    context = {"locations": results}
    return render(request, "members/events/locations.html#locations", context)


@login_required(redirect_field_name=LOGIN_URL, login_url=LOGIN_URL)
def show_location(request: HttpRequest, location_id: int):
    location = Location.objects.get(pk=location_id)
    siteinfo = SiteInfo.objects.get(id=1)
    context = {"location": location, "siteinfo": siteinfo}
    return render(
        request,
        template_name="members/events/show_location.html",
        context=context,
    )


@login_required(redirect_field_name=LOGIN_URL, login_url=LOGIN_URL)
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


@login_required(redirect_field_name=LOGIN_URL, login_url=LOGIN_URL)
def delete_location(request: HttpRequest, location_id: int):
    location = Location.objects.get(pk=location_id)
    location.delete()
    return redirect("location_list")


@login_required(redirect_field_name=LOGIN_URL, login_url=LOGIN_URL)
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
