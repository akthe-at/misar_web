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

    class Meta:
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


class MemberFile(models.Model):
    """A class to represent user-uploaded files"""

    class Meta:
        permissions = [
            ("share_memberfile", "Can share member file"),
        ]

    owner = models.ForeignKey(
        Member, on_delete=models.CASCADE, related_name="owned_files", null=False
    )
    file = models.FileField(upload_to="media/", null=False, blank=False)
    file_name = models.CharField(max_length=50)
    file_description = models.CharField(max_length=50)
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

