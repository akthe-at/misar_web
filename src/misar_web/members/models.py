from datetime import datetime
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.text import slugify
from uuid import uuid4
from localflavor.us.models import USZipCodeField
from guardian.shortcuts import assign_perm


class Member(AbstractUser):
    """Defines a member of the organization"""

    member_password = models.CharField(
        ("MISAR Secret Phrase"),
        max_length=15,
        blank=False,
    )
    first_name = models.CharField(("first name"), max_length=150, blank=True)
    last_name = models.CharField(("last name"), max_length=150, blank=True)
    email = models.EmailField(("email address"), blank=True)
    phone_number = models.CharField(max_length=20)
    address = models.CharField(max_length=200)
    city = models.CharField(max_length=50)
    zip_code = USZipCodeField(("zip_code"), null=False, max_length=10)
    date_of_birth = models.DateField(null=True, blank=True)

    class Meta:  # type: ignore
        verbose_name = "member"
        verbose_name_plural = "members"

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

    def save(self, *args, **kwargs):
        is_new = self.pk is None
        super().save(*args, **kwargs)
        if is_new:
            shared_files = MemberFile.objects.filter(share_with_all=True)
            for file in shared_files:
                assign_perm("members.view_memberfile", self, file)


class Location(models.Model):
    """A class to represent the location for events such as trainings, demos, fundraisers, etc."""

    point_of_contact = models.CharField(
        ("Location Point of Contact, if exists."), max_length=50, blank=True
    )
    phone_number = models.CharField(
        ("Location Phone Number"), max_length=50, blank=True
    )
    email = models.EmailField(("Location Email"), blank=True)
    name = models.CharField(("Location Name"), max_length=50)
    website = models.URLField(
        ("Location Website"),
        max_length=75,
        null=True,
        blank=True,
    )
    description = models.CharField(("Location Description"), max_length=50)
    address = models.CharField(("Address"), max_length=100)
    city = models.CharField(("City"), max_length=50)
    state = models.CharField(("State"), max_length=50)
    zip_code = USZipCodeField(("Zip Code"), null=False, max_length=10)
    misar_poc = models.ForeignKey(
        Member,
        on_delete=models.SET_NULL,
        related_name="misar_poc",
        null=True,
        blank=True,
        verbose_name="MISAR Point of Contact",
    )

    def __str__(self):
        return self.name


class MemberFile(models.Model):
    """A class to represent user-uploaded files"""

    class Meta:  # type: ignore
        permissions = [
            ("share_memberfile", "Can share member file"),
        ]

    owner = models.ForeignKey(
        Member, on_delete=models.CASCADE, related_name="owned_files", null=False
    )
    file = models.FileField(upload_to="media/", null=False, blank=False)
    file_name = models.CharField(("File Name"), max_length=50)
    file_description = models.CharField(("File Description"), max_length=50)
    date_created = models.DateTimeField(auto_now_add=True)
    last_modified = models.DateTimeField(auto_now=True)
    share_with_all = models.BooleanField(default=False)
    slug = models.SlugField(unique=True, editable=False, max_length=255)

    def __str__(self):
        return self.file_name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(f"{self.file_name}--{uuid4()}")
        user = kwargs.get("user")
        if user is not None:
            self.owner = user

        super().save(*args, **kwargs)


class Event(models.Model):
    """A class to represent events such as trainings, demos, fundraisers, etc."""

    event_poster = models.ForeignKey(Member, on_delete=models.CASCADE, null=True)
    date_posted = models.DateTimeField(auto_now_add=True)
    last_modified = models.DateTimeField(auto_now=True)
    event_organizer = models.ForeignKey(
        Member, on_delete=models.CASCADE, related_name="organized_events", null=True
    )
    event_name = models.CharField(("Event Name"), max_length=50)
    description = models.CharField(("Event Description"), max_length=50)
    event_type = models.CharField(("Event Type"), max_length=50)
    date = models.DateField(("Event Date"))
    location = models.ForeignKey(
        Location, on_delete=models.SET_NULL, related_name="event_location", null=True
    )
    start_time = models.TimeField(("Start Time"))
    end_time = models.TimeField(("End Time"), null=True, blank=True)
    special_instructions = models.TextField(
        ("Special Instructions"), max_length=500, blank=True
    )

    def __str__(self):
        return self.event_name


class ExternalReference(models.Model):
    """A class to represent external references for the organization"""

    class Meta:  # type: ignore
        verbose_name = "External Reference"
        verbose_name_plural = "External References"

    name = models.CharField(("Name"), max_length=50)
    description = models.CharField(("Description"), max_length=50)
    url = models.URLField(("URL"), max_length=75)

    def __str__(self):
        return self.name
