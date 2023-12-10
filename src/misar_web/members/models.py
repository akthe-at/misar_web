import uuid
from pathlib import Path

from django.contrib.auth.models import AbstractUser
from django.db import models, transaction
from django.utils.text import slugify
from localflavor.us.models import USZipCodeField


class Permission(models.Model):
    name = models.CharField(max_length=50)
    description = models.CharField(max_length=200)

    def __str__(self):
        return self.name


class Member(AbstractUser):
    """Defines a member of the organization"""

    member_password = models.CharField(
        ("MISAR Secret Phrase"), max_length=15, blank=False
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

    DEFAULT_PERMISSIONS = ["view", "edit", "delete", "share"]

    users = models.ManyToManyField(Member, related_name="owned_by")
    current_owner = models.ForeignKey(
        Member, related_name="owned_files", on_delete=models.CASCADE
    )
    file = models.FileField(upload_to="media/", null=False, blank=False)
    file_description = models.CharField(max_length=50)
    permissions = models.ManyToManyField(Permission, related_name="files")
    handle = models.SlugField(unique=True)
    date_created = models.DateTimeField(auto_now_add=True)
    last_modified = models.DateTimeField(auto_now=True)
    share_with_all = models.BooleanField(default=False)

    def __str__(self):
        return str(self.file)

    def save(self, *args, **kwargs):
        if not self.handle:
            base_slug = slugify(self.file_name)[:50]
            unique_slug = base_slug

            while MemberFile.objects.filter(handle=unique_slug).exists():
                unique_slug = f"{base_slug}-{uuid.uuid4().hex[:6]}"
            self.handle = unique_slug

        with transaction.atomic():
            super().save(*args, **kwargs)

            if not self.pk:
                # Save the instance first to get an id
                super().save(*args, **kwargs)

                # set default permissions when a new file is uploaded.
                for permission in self.DEFAULT_PERMISSIONS:
                    file_sharing = FileSharing(file=self, permission=permission)
                    file_sharing.save()
                    file_sharing.recipient.set(self.users.all())
            else:
                super().save(*args, **kwargs)

    def transfer_ownership(self, new_owner):
        FileOwnershipTransfer.objects.create(
            file=self, from_member=self.current_owner, to_member=new_owner
        )
        self.current_owner = new_owner
        self.save()

    class Meta:
        permissions = [
            ("view", "Can view file"),
            ("edit", "Can edit file"),
            ("delete", "Can delete file"),
            ("share", "Can share file"),
            ("revoke_share", "Can revoke file sharing"),
        ]


class FileSharing(models.Model):
    """Representation of File Sharing Permissions"""

    PERMISSION_CHOICES = [
        ("view", "Can view file"),
        ("edit", "Can edit file"),
        ("delete", "Can delete file"),
        ("share", "Can share file"),
    ]

    file = models.ForeignKey(MemberFile, on_delete=models.CASCADE)
    recipient = models.ManyToManyField(Member, related_name="file_sharings")
    permission = models.CharField(choices=PERMISSION_CHOICES, max_length=20)
    date_shared = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return f"{self.file} is shared with {self.recipient}"

    def save(self, *args, **kwargs):
        # set default permissions when a file is shared
        if not self.pk and not self.permission:
            self.permission = "view"
        super().save(*args, **kwargs)


class FileOwnershipTransfer(models.Model):
    file = models.ForeignKey(MemberFile, on_delete=models.CASCADE)
    from_members = models.ManyToManyField(
        Member, related_name="ownership_transfers_sent"
    )
    to_members = models.ManyToManyField(
        Member, related_name="ownership_transfers_received"
    )
    date_requested = models.DateTimeField(auto_now_add=True)
    date_completed = models.DateTimeField(null=True, blank=True)
    is_completed = models.BooleanField(default=False)
