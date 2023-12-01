from django.db import models
from django.contrib.auth.models import AbstractUser
from localflavor.us.models import USStateField, USZipCodeField


class Member(AbstractUser):
    """Defines a member of the organization"""

    first_name = models.CharField(("first name"), max_length=150, blank=True)
    last_name = models.CharField(("last name"), max_length=150, blank=True)
    email = models.EmailField(("email address"), blank=True)
    phone_number = models.CharField(max_length=20)
    address = models.CharField(max_length=200)
    city = models.CharField(max_length=50)
    state = USStateField(("state"), null=False)
    zip_code = USZipCodeField(("zip_code"), null=False, max_length=10)
    date_of_birth = models.DateField(null=True, blank=True)

    class Meta:
        verbose_name = "member"
        verbose_name_plural = "members"

    def __str__(self):
        return f"{self.first_name} {self.last_name}"


class MemberFile(models.Model):
    """A class to represet user-uploaded files"""

    file_object = models.FileField(upload_to="members/member_files/")

