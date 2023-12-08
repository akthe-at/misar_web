from django.http import HttpRequest
from django.shortcuts import render

from .models import SearchSpecialty, SiteInfo


def home(request: HttpRequest):
    siteinfo = SiteInfo.objects.get(id=1)
    search_spec = SearchSpecialty.objects.all()
    context = {"siteinfo": siteinfo, "search_spec": search_spec}
    return render(request=request, template_name="home/home.html", context=context)


def donate(request: HttpRequest):
    site_info = SiteInfo.objects.get(id=1)
    context = {"siteinfo": site_info, "donate": donate}
    return render(request=request, template_name="home/donate.html", context=context)


def contact(request: HttpRequest):
    site_info = SiteInfo.objects.get(id=1)
    context = {"siteinfo": site_info}
    return render(request=request, template_name="home/contact.html", context=context)

