from django.urls import reverse_lazy
from django.views.generic import CreateView
from misar_web.settings import LOGIN_URL
from .forms import FileUploadForm, MemberRegistrationForm
from .models import MemberFile
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect


class MemberRegisterView(CreateView):
    form_class = MemberRegistrationForm
    template_name = "registration/register.html"
    success_url = reverse_lazy("login")


@login_required(redirect_field_name=LOGIN_URL, login_url=LOGIN_URL)
def member_home(request):
    return render(request, "members/member_landing.html")


@login_required(redirect_field_name=LOGIN_URL, login_url=LOGIN_URL)
def files(request):
    member_files = MemberFile.objects.filter(current_owner=request.user)
    shared_files = MemberFile.objects.filter(users=request.user)
    context = {
        "memberfiles": member_files,
        "sharedfiles": shared_files,
    }
    return render(request, "members/files.html", context)


# class FileListView(ListView):
#     """View for seeing team/member files"""
#
#     model = MemberFile
#     template_name = "members/files.html"
#     context_object_name = "files"


# @login_required(redirect_field_name=LOGIN_URL, login_url=LOGIN_URL)
# class UploadFileView(CreateView):
#     """View for uploading member files"""
#
#     model = MemberFile
#     form_class = FileUploadForm
#     template_name = "members/upload.html"
#     success_url = reverse_lazy("files")


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

