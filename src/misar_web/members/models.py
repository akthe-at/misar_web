from django.db import models
from django.contrib.auth.models import AbstractUser
from localflavor.us.models import USZipCodeField


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

    user = models.ForeignKey(Member, on_delete=models.CASCADE)
    file = models.FileField(upload_to="members/member_files/", null=False, blank=False)
    date_created = models.DateTimeField(auto_now_add=True)
    date_modified = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return f"{self.file}"

    def delete(self, *args, **kwargs):
        super().delete(self, *args, **kwargs)

    class Meta:
        permissions = [
            ("view_file", "Can view file"),
            ("edit_file", "Can edit file"),
            ("delete_file", "Can delete file"),
        ]


class FileSharing(models.Model):
    """Representation of File Sharing Permissions"""

    file = models.ForeignKey(MemberFile, on_delete=models.CASCADE)
    recipient = models.ForeignKey(Member, on_delete=models.CASCADE)
    date_shared = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return f"{self.file} is shared with {self.recipient}"

