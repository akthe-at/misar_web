from django.http import HttpRequest
from django.shortcuts import render

from .models import SiteInfo


def home(request: HttpRequest):
    site_info = SiteInfo.objects.get(id=1)
    return render(request, "home/home.html", {"siteinfo": site_info})

