from django.http import HttpRequest
from django.shortcuts import render

from .models import SiteInfo, TeamGoals


def home(request: HttpRequest):
    site_info = SiteInfo.objects.get(id=1)
    team_goals = TeamGoals.objects.all()
    context = {"siteinfo": site_info, "team_goals": team_goals}
    return render(request=request, template_name="home/home.html", context=context)


def donate(request: HttpRequest):
    context = {"donate": donate}
    return render(request=request, template_name="home/donate.html", context=context)


def contact(request: HttpRequest):
    site_info = SiteInfo.objects.get(id=1)
    context = {"siteinfo": site_info}
    return render(request=request, template_name="home/contact.html", context=context)

