import csv
from typing import Any, Literal, Mapping

from django.contrib import messages
from django.db.models import QuerySet
from django.http.response import HttpResponseRedirect
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
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
from django.http import HttpRequest, HttpResponse, HttpResponseForbidden, FileResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import CreateView
from guardian.shortcuts import (
    assign_perm,
    get_objects_for_user,
    get_perms,
)
from home.models import SiteInfo
from misar_web.settings import LOGIN_URL

from .forms import (
    EventForm,
    EventLocationForm,
    FileShareForm,
    FileUploadForm,
    MemberRegistrationForm,
)
from .models import Event, ExternalReference, Location, Member, MemberFile, TeamFile


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
def member_home(request: HttpRequest) -> HttpResponse:
    siteinfo: SiteInfo = SiteInfo.objects.get(id=1)
    external_references: QuerySet[ExternalReference] = (
        ExternalReference.objects.all().order_by("name")
    )
    team_files: QuerySet[TeamFile] = TeamFile.objects.all().order_by("file_name")
    context: Mapping[str, Any] = {
        "siteinfo": siteinfo,
        "external_references": external_references,
        "team_files": team_files,
    }
    return render(
        request=request, template_name="members/member_landing.html", context=context
    )


@login_required(redirect_field_name=LOGIN_URL, login_url=LOGIN_URL)
def files(request: HttpRequest) -> HttpResponse | HttpResponseRedirect:
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
                request, "members/files.html#personal_table", {"memberfiles": files}
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
def update_shared_files(request: HttpRequest) -> HttpResponse:
    files = get_objects_for_user(
        request.user, "view_memberfile", klass=MemberFile
    ).exclude(owner=request.user)
    return render(
        request, "members/files.html#shared-files-table", {"sharedfiles": files}
    )


@login_required(redirect_field_name=LOGIN_URL, login_url=LOGIN_URL)
def update_files(request: HttpRequest) -> HttpResponse:
    files = MemberFile.objects.filter(owner=request.user).order_by("id")
    return render(request, "members/files.html#personal_table", {"memberfiles": files})


@require_http_methods(["DELETE"])
@login_required(redirect_field_name=LOGIN_URL, login_url=LOGIN_URL)
def delete_file(request: HttpRequest, file_id: int) -> HttpResponse | None:
    file = MemberFile.objects.get(pk=file_id)
    if request.user == file.owner or request.user.has_perm(
        "members.delete_memberfile", file
    ):
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
            request, "members/files.html#personal_table", {"memberfiles": files}
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

    return FileResponse(open(file.file.path, "rb"), as_attachment=True)


class ShareFileView(LoginRequiredMixin, View):
    login_url = LOGIN_URL
    redirect_field_name = "redirect_to"

    def get(self, request, file_id=None):
        siteinfo: SiteInfo = SiteInfo.objects.get(id=1)
        file_instance = None
        if file_id is not None:
            try:
                file_instance = MemberFile.objects.get(id=file_id)
            except MemberFile.DoesNotExist:
                return HttpResponseForbidden("File does not exist.")
        form: FileShareForm = FileShareForm(
            initial={"file": file_instance}, user=request.user
        )
        context: Mapping[str, Any] = {"form": form, "siteinfo": siteinfo}
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
def all_events(request: HttpRequest):
    siteinfo = SiteInfo.objects.get(id=1)
    event_types = Event.objects.values_list("event_type", flat=True).distinct()
    events = Event.objects.filter(date__gte=timezone.now()).order_by("date")

    if request.method == "POST":
        selected_type = request.POST.get("event_type")
        if selected_type:
            events = events.filter(event_type=selected_type)

    context = {"siteinfo": siteinfo, "events": events, "event_types": event_types}
    return render(request, "members/events/all_events.html", context)


@login_required(redirect_field_name=LOGIN_URL, login_url=LOGIN_URL)
def filter_events(request: HttpRequest):
    event_type = request.GET.get("event_type")
    if event_type:
        events = Event.objects.filter(event_type=event_type).filter(
            date__gte=timezone.now()
        )
    else:
        events = Event.objects.all().filter(date__gte=timezone.now())
    return render(
        request, "members/events/all_events.html#event_list", {"events": events}
    )


@login_required(redirect_field_name=LOGIN_URL, login_url=LOGIN_URL)
def create_event(request: HttpRequest):
    DEFAULT_PERMS = [
        "add_event",
        "change_event",
        "delete_event",
    ]
    siteinfo = SiteInfo.objects.get(id=1)

    event_form = EventForm(request.POST or None)
    if request.method == "POST":
        if event_form.is_valid():
            event = event_form.save(commit=False)
            event.event_poster = request.user
            event.save()
            for permission in DEFAULT_PERMS:
                assign_perm(permission, request.user, event)
                request.user.save()
                assign_perm(permission, event.event_organizer, event)
                event.event_organizer.save()
            # TODO: Fix moderator permission assignments
            # moderator_group, created = Group.objects.get_or_create(name="moderator")
            # assign_perm(DEFAULT_PERMS, moderator_group, event)
            events = Event.objects.filter(date__gte=timezone.now()).order_by("date")
            context = {"siteinfo": siteinfo, "events": events}
            return render(request, "members/events/all_events.html#event_list", context)
    context = {"siteinfo": siteinfo, "event_form": event_form}
    return render(request, "members/events/all_events.html#add_event_modal", context)


@login_required(redirect_field_name=LOGIN_URL, login_url=LOGIN_URL)
def update_event(request: HttpRequest, event_id: int):
    siteinfo = SiteInfo.objects.get(id=1)
    event = Event.objects.get(pk=event_id)
    if request.method == "POST":
        form = EventForm(request.POST, instance=event)
        if form.is_valid():
            form.save()
            events = Event.objects.filter(date__gte=timezone.now()).order_by("date")
            context = {"siteinfo": siteinfo, "events": events}
            return render(request, "members/events/all_events.html#event_list", context)
        return render(request, "members/events/all_events.html#failure")
    form = EventForm(instance=event)
    context = {"siteinfo": siteinfo, "form": form, "event": event}
    return render(request, "members/events/all_events.html#edit_event_modal", context)


@login_required(redirect_field_name=LOGIN_URL, login_url=LOGIN_URL)
def delete_event(request: HttpRequest, event_id: int):
    if request.user.has_perm("members.delete_event"):
        event = Event.objects.get(pk=event_id)
        event.delete()
    else:
        messages.error(request, "You do not have permission to delete this event.")
    siteinfo = SiteInfo.objects.get(id=1)
    events = Event.objects.filter(date__gte=timezone.now()).order_by("date")
    context = {"siteinfo": siteinfo, "events": events}
    return render(request, "members/events/all_events.html#event_list", context)


@login_required(redirect_field_name=LOGIN_URL, login_url=LOGIN_URL)
def create_location(request: HttpRequest):
    DEFAULT_PERMS = ("add_location", "change_location", "delete_location")
    submitted = False
    siteinfo = SiteInfo.objects.get(id=1)
    if request.method == "POST":
        form = EventLocationForm(request.POST)
        if form.is_valid():
            form.save()
            location, _ = Location.objects.get_or_create(
                point_of_contact=form.cleaned_data["point_of_contact"],
                phone_number=form.cleaned_data["phone_number"],
                email=form.cleaned_data["email"],
                name=form.cleaned_data["name"],
                website=form.cleaned_data["website"],
                description=form.cleaned_data["description"],
                address=form.cleaned_data["address"],
                city=form.cleaned_data["city"],
                state=form.cleaned_data["state"],
                zip_code=form.cleaned_data["zip_code"],
                misar_poc=form.cleaned_data["misar_poc"],
            )
            for permission in DEFAULT_PERMS:
                assign_perm(permission, request.user, location)
                request.user.save()
            # redirect to list_locations
        events = Event.objects.filter(date__gte=timezone.now()).order_by("date")
        context = {"siteinfo": siteinfo, "events": events}
        return render(request, "members/events/all_events.html#event_list", context)
    else:
        form = EventLocationForm()
        if "submitted" in request.GET:
            submitted = True

    context = {"siteinfo": siteinfo, "form": form, "submitted": submitted}
    if str(request.headers.get("Referer")).endswith("/members/events/locations/"):
        return render(request, "members/events/add_location.html", context)
    return render(
        request, "members/events/all_events.html#add_event_location_modal", context
    )


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
def show_location(request: HttpRequest, location_id: int) -> HttpResponse:
    location: Location = Location.objects.get(pk=location_id)
    desired_perms: tuple[Literal["change_location"], ["delete_location"]] = (
        "change_location",
        "delete_location",
    )
    perms: dict[str, bool] = {
        perm: request.user.has_perm(perm, location) for perm in desired_perms
    }
    context: dict[str, Location | dict[str, bool]] = {
        "location": location,
        "perms": perms,
    }
    return render(
        request=request,
        template_name="members/events/locations.html#show_location",
        context=context,
    )


@login_required(redirect_field_name=LOGIN_URL, login_url=LOGIN_URL)
def update_location(request: HttpResponse, location_id: int):
    location = Location.objects.get(pk=location_id)
    siteinfo = SiteInfo.objects.get(id=1)
    if not request.user.has_perm("members.change_location", location):
        messages.error(request, "You do not have permission to update this location.")
        return redirect("location_list")
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
    if request.user.has_perm("members.delete_location", location):
        location.delete()
    else:
        messages.error(request, "You do not have permission to delete this location.")
    siteinfo = SiteInfo.objects.get(id=1)
    location_list = Location.objects.all().order_by("name")
    context = {"siteinfo": siteinfo, "locations": location_list}
    return render(request, "members/events/locations.html#locations", context)


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
    else:
        pass
