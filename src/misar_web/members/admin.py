from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from guardian.admin import GuardedModelAdmin

from .models import (
    Event,
    ExternalReference,
    Location,
    Member,
    MemberFile,
    TeamFile,
    TeamFileCategory,
)

# Register your models here.


class CustomUserAdmin(UserAdmin):
    fieldsets = (
        *UserAdmin.fieldsets,
        (
            "Additional Info",
            {
                "fields": (
                    "phone_number",
                    "address",
                    "city",
                    "date_of_birth",
                )
            },
        ),
    )


@admin.register(TeamFileCategory)
class TeamFileCategoryAdmin(admin.ModelAdmin):
    search_fields = ("category_name", "category_description")
    list_display = ("category_name", "category_description")
    ordering = ("category_name", "date_created")


@admin.register(TeamFile)
class TeamFileAdmin(admin.ModelAdmin):
    search_fields = ("file_name", "file_description", "date_created")
    list_display = (
        "file_name",
        "file",
        "file_description",
        "date_created",
        "last_modified",
    )
    ordering = ("-date_created",)


class MemberFileAdmin(GuardedModelAdmin):
    search_fields = ("file_name", "file_description", "owner")
    list_display = ("file_name", "file", "file_description", "owner", "date_created")
    ordering = ("-date_created",)


admin.site.register(Member, CustomUserAdmin)
admin.site.register(MemberFile, MemberFileAdmin)


@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    list_display = ("name", "address", "city", "state", "zip_code")
    list_filter = ("name", "city", "state", "zip_code")
    search_fields = (
        "name",
        "address",
        "city",
    )
    ordering = ("name", "city", "state", "zip_code")


class EventAdmin(GuardedModelAdmin):
    list_display = (
        "event_name",
        "event_type",
        "location",
        "date",
        "start_time",
        "end_time",
        "event_organizer",
    )
    list_filter = ("event_name", "location", "date")
    search_fields = (
        "event_name",
        "event_type",
        "location",
    )
    ordering = ("event_name", "event_type", "location", "date")


admin.site.register(Event, EventAdmin)


@admin.register(ExternalReference)
class ExternalRefAdmin(admin.ModelAdmin):
    list_display = ("name", "url")
    list_filter = ("name", "url")
    search_fields = (
        "name",
        "url",
    )
    ordering = ("name", "url")
