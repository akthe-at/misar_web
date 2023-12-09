from datetime import datetime
from typing import Any

from django import forms
from django.contrib.auth.forms import UserCreationForm
from localflavor.us.forms import USZipCodeField

from members.models import Member, MemberFile


class MemberRegistrationForm(UserCreationForm):
    """MISAR Member Registration Form"""

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super(MemberRegistrationForm, self).__init__(*args, **kwargs)
        self.fields["password1"].widget.attrs["class"] = "form-control"
        self.fields["password2"].widget.attrs["class"] = "form-control"

    username = forms.CharField(widget=forms.TextInput(attrs={"class": "form-control"}))
    member_password = forms.CharField(
        max_length=15, widget=forms.PasswordInput(attrs={"class": "form-control"})
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
        fields = UserCreationForm.Meta.fields + (
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
        fields = ("file", "file_name")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs["class"] = "input_css_class"

    def save(self, *args, **kwargs):
        instance = super().save(commit=False)
        return instance
