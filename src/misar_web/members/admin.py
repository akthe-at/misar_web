from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import FilePermission, Member, MemberFile
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


admin.site.register(Member, CustomUserAdmin)
admin.site.register([MemberFile, FilePermission])

