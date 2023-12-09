from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.views.generic import CreateView

from misar_web.settings import LOGIN_URL
from home.models import SiteInfo
from .forms import FileUploadForm, MemberRegistrationForm
from .models import MemberFile


class MemberRegisterView(CreateView):
    form_class = MemberRegistrationForm
    template_name = "registration/register.html"
    success_url = reverse_lazy("login")


@login_required(redirect_field_name=LOGIN_URL, login_url=LOGIN_URL)
def member_home(request):
    siteinfo = SiteInfo.objects.get(id=1)
    context = {"siteinfo": siteinfo}
    return render(request, "members/member_landing.html", context)


@login_required(redirect_field_name=LOGIN_URL, login_url=LOGIN_URL)
def files(request):
    member_files = MemberFile.objects.filter(current_owner=request.user)
    shared_files = MemberFile.objects.filter(users=request.user)
    context = {
        "memberfiles": member_files,
        "sharedfiles": shared_files,
    }
    return render(request, "members/files.html", context)


@login_required(redirect_field_name=LOGIN_URL, login_url=LOGIN_URL)
def delete_file(request, file_id):
    file = MemberFile.objects.get(pk=file_id)
    if request.user == file.current_owner or request.user.has_perm("delete_file", file):
        file.delete()
        return redirect("files")
    return HttpResponseForbidden("You do not have permission to delete this file.")


def file_upload(request):
    context = {}
    form = FileUploadForm(request.POST or None, request.FILES or None)
    if form.is_valid():
        obj = form.save(commit=False)
        if request.user.is_authenticated:
            obj.user = request.user
            obj.current_owner = request.user
            obj.save()
            return redirect("files")
        form.add_error(None, "You must be logged in to upload files.")
    context["form"] = form
    return render(request, "members/upload.html", context)

