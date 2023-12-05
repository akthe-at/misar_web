from django.contrib import admin
from .models import SiteInfo, SearchSpecialty
# Register your models here.

admin.site.register([SiteInfo, SearchSpecialty])

