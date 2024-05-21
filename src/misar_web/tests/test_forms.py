import pytest
from members.forms import EventLocationForm
from members.models import Location


@pytest.mark.django_db
class TestLocationForm:
    def test_location_created(self):
        """A submission to the Event Location Creation form creates and saves a location"""

        point_of_contact = "John Doe"
        phone_number = "123-456-7890"
        email = "JohnDoe@JohnDeere.com"
        name = "Jim's Farm"
        website = "www.jimsfarm.com"
        description = "A farm"
        address = "123 Main St"
        city = "Anytown"
        state = "PA"
        zip_code = "12345"
        misar_poc = None
        data = {
            "point_of_contact": point_of_contact,
            "phone_number": phone_number,
            "email": email,
            "name": name,
            "website": website,
            "description": description,
            "address": address,
            "city": city,
            "state": state,
            "zip_code": zip_code,
            "misar_poc": misar_poc,
        }
        form = EventLocationForm(data=data)
        if form.is_valid():
            form.save()
            assert Location.objects.filter(email=email).count() == 1

    def test_bad_location_email(self):
        """A submission to the Event Location Creation form with a bad email fails"""
        point_of_contact = "John Doe"
        phone_number = "123-456-7890"
        email = "JohnDoeJohnDeere.com"
        name = None
        website = "www.jimsfarm.com"
        description = "A farm"
        address = "123 Main St"
        city = "Anytown"
        state = "PA"
        zip_code = "12345"
        misar_poc = None
        data = {
            "point_of_contact": point_of_contact,
            "phone_number": phone_number,
            "email": email,
            "name": name,
            "website": website,
            "description": description,
            "address": address,
            "city": city,
            "state": state,
            "zip_code": zip_code,
            "misar_poc": misar_poc,
        }
        form = EventLocationForm(data=data)
        assert not form.is_valid()
        assert form.errors == {
            "email": ["Enter a valid email address."],
            "name": ["This field is required."],
        }
