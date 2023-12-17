from datetime import datetime
from typing import Any

from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.db import transaction
from localflavor.us.forms import USZipCodeField

from members.models import FilePermission, Member, MemberFile


class MemberRegistrationForm(UserCreationForm):
    """MISAR Member Registration Form"""

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super(MemberRegistrationForm, self).__init__(*args, **kwargs)
        self.fields["password1"].widget.attrs["class"] = "form-control"
        self.fields["password2"].widget.attrs["class"] = "form-control"

    username = forms.CharField(widget=forms.TextInput(attrs={"class": "form-control"}))
    member_password = forms.CharField(
        max_length=15,
        widget=forms.PasswordInput(attrs={"class": "form-control"}),
        help_text="Code Supplied by MISAR to enable Registration.",
        label="MISAR Member Secret-Phrase",
    )
    first_name = forms.CharField(
        widget=forms.TextInput(attrs={"class": "form-control"})
    )
    last_name = forms.CharField(widget=forms.TextInput(attrs={"class": "form-control"}))
    email = forms.EmailField(widget=forms.EmailInput(attrs={"class": "form-control"}))
    phone_number = forms.CharField(
        widget=forms.TextInput(attrs={"class": "form-control"})
    )
    address = forms.CharField(widget=forms.TextInput(attrs={"class": "form-control"}))
    city = forms.CharField(widget=forms.TextInput(attrs={"class": "form-control"}))
    zip = USZipCodeField(widget=forms.NumberInput(attrs={"class": "form-control"}))
    date_of_birth = forms.DateField(
        widget=forms.SelectDateWidget(
            years=range(1940, datetime.now().year),
            attrs={"class": "form-control"},
        )
    )

    def clean_member_password(self):
        """Checks to see if correct member password used to allow for registration"""

        data = self.cleaned_data["member_password"]
        if (
            data != "bigfishy"
        ):  # TODO: This needs to be written to an environmental variable before production
            raise forms.ValidationError(
                "Sorry you must have the secret code to become a MISAR member."
            )
        return data

    class Meta(UserCreationForm.Meta):
        model = Member
        fields = UserCreationForm.Meta.fields + (  # ignore
            "member_password",
            "first_name",
            "last_name",
            "email",
            "phone_number",
            "address",
            "city",
            "zip",
            "date_of_birth",
        )


input_css_class = "form-control"


class FileUploadForm(forms.ModelForm):
    """Form for members to upload files"""

    class Meta:
        model = MemberFile
        fields = ("file", "file_name", "file_description", "share_with_all")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs["class"] = "input_css_class"

    def save(self, owner: Member | None = None, *args, **kwargs):
        with transaction.atomic():
            instance = super().save(commit=False)

            # Set the owner field to the authenticated user
            instance.owner = owner

            instance.save()

            if kwargs.get("commit", True):  # Only do this if commit is True
                if instance.share_with_all:
                    print("Sharing with all users...")
                    instance.share_with_all_users()

        return instance


class FilePermissionForm(forms.ModelForm):
    """Form for sharing files with other users"""

    recipient = forms.ModelChoiceField(
        queryset=Member.objects.all(),
        widget=forms.Select,
    )
    permissions = forms.MultipleChoiceField(
        choices=FilePermission.PERMISSION_CHOICES,
        widget=forms.CheckboxSelectMultiple,
    )

    file = forms.ModelChoiceField(
        queryset=MemberFile.objects.all(),
        widget=forms.Select,
    )

    def __init__(self, *args, **kwargs):
        user = kwargs.pop("user", None)
        super(FilePermissionForm, self).__init__(*args, **kwargs)
        if user:
            # update queryset based on your models
            self.fields["file"].queryset = MemberFile.objects.filter(owner=user)
            self.fields["recipient"].queryset = Member.objects.exclude(
                id=user.id
            ).exclude(is_superuser=True)

    class Meta:
        model = FilePermission
        fields = ["file", "recipient", "permissions"]

