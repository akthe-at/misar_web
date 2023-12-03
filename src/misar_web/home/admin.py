from django.contrib import admin
from .models import SiteInfo, TeamGoals
# Register your models here.

admin.site.register([SiteInfo, TeamGoals])

