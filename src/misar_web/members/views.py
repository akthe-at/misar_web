from django.core.files.storage import FileSystemStorage
from django.views import generic
from django.urls import reverse_lazy
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required

from misar_web.settings import LOGIN_URL
from .forms import MemberRegistrationForm, FileUploadForm
from .models import MemberFile


class MemberRegisterView(generic.CreateView):
    form_class = MemberRegistrationForm
    template_name = "registration/register.html"
    success_url = reverse_lazy("login")


@login_required(redirect_field_name=LOGIN_URL, login_url=LOGIN_URL)
def member_landing(request):
    return render(request, template_name="members/member_landing.html")


@login_required
def file_upload(request):
    # context = {}
    if request.method == "POST":
        form = FileUploadForm(request.POST, request.FILES)
        if form.is_valid():
            new_file = form.save(commit=False)
            new_file.user = request.user
            new_file.save()
            return redirect("file_list")
    else:
        form = FileUploadForm()
        # uploaded_file = request.FILES["document"]
        # file_store = FileSystemStorage()
        # name = file_store.save(uploaded_file.name, uploaded_file)
        # context["url"] = file_store.url(name)
    return render(
        request, template_name="members/upload_file.html", context={"form": form}
    )


@login_required
def file_list(request):
    files = MemberFile.objects.filter(user=request.user)
    context = {"files": files}
    return render(request, "members/files.html", context)

