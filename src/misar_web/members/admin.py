from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from guardian.admin import GuardedModelAdmin
from .models import Member, MemberFile
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
    search_fields = ("file_name", "file_description")
    list_display = ("file_name", "file_description", "owner", "date_created")
    ordering = ("-date_created",)


admin.site.register(Member, CustomUserAdmin)
admin.site.register(MemberFile, MemberFileAdmin)

