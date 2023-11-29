from django.http import HttpRequest
from django.shortcuts import render

from .models import SiteInfo


def home(request: HttpRequest):
    site_info = SiteInfo.objects.get(id=1)
    return render(
        request, template_name="home/home.html", context={"siteinfo": site_info}
    )


def donate(request: HttpRequest):
    return render(request, template_name="home/donate.html", context={"donate": donate})

