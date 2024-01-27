from datetime import datetime
from typing import Any

from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.core.exceptions import ValidationError
from django.db import transaction
from guardian.shortcuts import assign_perm, get_objects_for_user
from localflavor.us.forms import USZipCodeField

from members.models import Event, Location, Member, MemberFile


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
            raise ValidationError(
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
        fields = ("file", "file_name", "file_description", "share_with_all")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["file"].required = True
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
                    for member in Member.objects.all():
                        assign_perm("view_memberfile", member, instance)

        return instance


class FileShareForm(forms.ModelForm):
    """Form for sharing files with other users"""

    PERMISSION_CHOICES = (
        ("view_memberfile", "View"),
        ("change_memberfile", "Change"),
        ("delete_memberfile", "Delete"),
        ("share_memberfile", "Share"),
    )

    class Meta:
        model = MemberFile
        fields = ["file", "recipient", "assign_to_all", "permissions"]

    recipient = forms.ModelMultipleChoiceField(
        queryset=Member.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=False,
    )
    assign_to_all = forms.BooleanField(required=False)

    file = forms.ModelChoiceField(
        queryset=MemberFile.objects.all(),
        widget=forms.Select,
    )

    permissions = forms.MultipleChoiceField(
        widget=forms.CheckboxSelectMultiple,
        choices=(
            ("view_memberfile", "View"),
            ("change_memberfile", "Change"),
            ("delete_memberfile", "Delete"),
            ("share_memberfile", "Share"),
        ),
    )

    def __init__(self, *args, **kwargs):
        user = kwargs.pop("user", None)
        super(FileShareForm, self).__init__(*args, **kwargs)
        if user:
            # update queryset based on your models
            self.fields["file"].queryset = get_objects_for_user(
                user, "share_memberfile", klass=MemberFile
            )
            self.fields["recipient"].queryset = Member.objects.exclude(
                id=user.id
            ).exclude(is_superuser=True)

    def clean(self):
        cleaned_data = super().clean()
        assign_to_all = cleaned_data.get("assign_to_all")
        recipient = cleaned_data.get("recipient")
        if assign_to_all and recipient:
            raise ValidationError(
                'You cannot both, "Assign to All" and "select specific users" at the same time.'
            )
        if not assign_to_all and not recipient:
            raise ValidationError(
                "You must either 'Assign to all' or select specific users"
            )

    def save(self, owner: Member | None = None, *args, **kwargs):
        recipients = self.cleaned_data["recipient"]
        file = self.cleaned_data["file"]
        permissions = self.cleaned_data["permissions"]
        for recipient in recipients:
            for permission in permissions:
                assign_perm(permission, recipient, file)


class EventLocationForm(forms.ModelForm):
    """Form for members to create event locations"""

    class Meta:
        model = Location
        fields = [
            "point_of_contact",
            "phone_number",
            "email",
            "name",
            "website",
            "description",
            "address",
            "city",
            "state",
            "zip_code",
            "misar_poc",
        ]

    website = forms.URLField(required=False, assume_scheme="https")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["misar_poc"].queryset = Member.objects.filter(is_superuser=False)
        for field in self.fields:
            self.fields[field].widget.attrs["class"] = "input_css_class"


class DateTimePickerInput(forms.DateInput):
    input_type = "datetime"


class EventForm(forms.ModelForm):
    """Form for members to create events"""

    EVENT_TYPES = (
        ("Training", "Training"),
        ("Demo", "Demo"),
        ("Fundraiser", "Fundraiser"),
        ("Camp", "Camp"),
        ("Testing", "Testing"),
        ("Other", "Other"),
    )

    class Meta:
        model = Event
        fields = [
            "event_organizer",
            "event_name",
            "location",
            "description",
            "event_type",
            "date",
            "start_time",
            "end_time",
            "special_instructions",
        ]

    event_type = forms.ChoiceField(widget=forms.RadioSelect, choices=EVENT_TYPES)
    date = forms.DateField(widget=forms.DateInput(attrs={"type": "date"}))
    start_time = forms.TimeField(widget=forms.TimeInput(attrs={"type": "time"}))
    end_time = forms.TimeField(widget=forms.TimeInput(attrs={"type": "time"}))

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class LocationCSVForm(forms.Form):
    """Form for uploading a CSV file of locations"""

    locations = forms.ModelMultipleChoiceField(
        queryset=Location.objects.all(), widget=forms.CheckboxSelectMultiple
    )
