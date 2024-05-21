from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from guardian.admin import GuardedModelAdmin
from .models import ExternalReference, Member, MemberFile, Location, Event
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
