from django.http import HttpRequest
from django.shortcuts import render

from .models import SearchSpecialty, SiteInfo


def home(request: HttpRequest):
    siteinfo = SiteInfo.objects.only(
        "id",
        "site_name",
        "tagline",
        "description",
        "dispatch_number",
        "mission_statement",
        "logo",
        "alternate_logo",
        "home_page_image",
        "donation_link",
        "team_email",
        "blank_icon",
    ).get(id=1)
    search_spec = SearchSpecialty.objects.all()
    context = {"siteinfo": siteinfo, "search_spec": search_spec}
    return render(request=request, template_name="home/home.html", context=context)


def icon_modal(request: HttpRequest, spec_id: int):
    specialty = SearchSpecialty.objects.get(pk=spec_id)
    return render(
        request, "home/home.html#search_spec_modal", context={"specialty": specialty}
    )


def donate(request: HttpRequest):
    siteinfo = SiteInfo.objects.get(id=1)
    context = {"siteinfo": siteinfo, "donate": donate}
    return render(request=request, template_name="home/donate.html", context=context)


def contact(request: HttpRequest):
    siteinfo = SiteInfo.objects.get(id=1)
    context = {"siteinfo": siteinfo}
    return render(request=request, template_name="home/contact.html", context=context)


def about(request: HttpRequest):
    siteinfo = SiteInfo.objects.get(id=1)
    context = {"siteinfo": siteinfo}
    return render(request=request, template_name="home/about.html", context=context)
