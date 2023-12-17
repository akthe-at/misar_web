from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.text import slugify
from uuid import uuid4
from localflavor.us.models import USZipCodeField


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


class MemberFile(models.Model):
    """A class to represent user-uploaded files"""

    owner = models.ForeignKey(
        Member, on_delete=models.CASCADE, related_name="owned_files", null=False
    )
    shared_with = models.ManyToManyField(
        Member,
        through="FilePermission",
        related_name="owned_by",
        through_fields=("file", "recipient"),
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

        for permission_choice in FilePermission.PERMISSION_CHOICES:
            for member in self.shared_with.all():
                FilePermission.objects.get_or_create(
                    file=self, user=member, permission=permission_choice[0]
                )

    def share_with_all_users(self):
        print("sharing with all users at the model level...")
        for member in Member.objects.all():
            file_permission, created = FilePermission.objects.get_or_create(
                file=self, user=member, permission=FilePermission.VIEW
            )
            print("FilePermission instance:", file_permission, "Created:", created)


class FilePermission(models.Model):
    """Representation of File Sharing Permissions"""

    VIEW = "view"
    SHARE = "share"
    EDIT = "change"  # Make sure "change" is included in your choices
    DELETE = "delete"

    PERMISSION_CHOICES = (
        (VIEW, "View"),
        (SHARE, "Share"),
        (EDIT, "Edit"),
        (DELETE, "Delete"),
    )
    file = models.ForeignKey(MemberFile, on_delete=models.CASCADE)
    recipient = models.ForeignKey(Member, on_delete=models.CASCADE)
    permissions = models.CharField(
        max_length=20, choices=PERMISSION_CHOICES, default=VIEW
    )
    date_shared = models.DateTimeField(auto_now_add=True)
    is_owner = models.BooleanField(default=False)

