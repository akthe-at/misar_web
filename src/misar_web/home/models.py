from django.db import models


class SiteInfo(models.Model):
    site_name = models.CharField(max_length=125)
    tagline = models.CharField(max_length=200)
    description = models.TextField()
    mission_statement = models.TextField()
    dispatch_number = models.CharField(default="(800)-818-5645", max_length=20)
    logo = models.ImageField(upload_to="home/files/images")
    alternate_logo = models.ImageField(upload_to="home/files/images")
    home_page_image = models.ImageField(upload_to="home/files/images")
    donation_link = models.CharField(max_length=250)
    street_address = models.CharField(max_length=50)
    po_box = models.CharField(max_length=20)
    city_state_zip = models.CharField(max_length=50)
    team_email = models.EmailField(max_length=50)
    about_photo_1 = models.ImageField(upload_to="home/files/images")
    about_photo_2 = models.ImageField(upload_to="home/files/images")
    about_photo_3 = models.ImageField(upload_to="home/files/images")
    just_a_dog_photo = models.ImageField(upload_to="home/files/images")
    misar_services_1 = models.ImageField(upload_to="home/files/images")
    misar_services_2 = models.ImageField(upload_to="home/files/images")
    misar_services_3 = models.ImageField(upload_to="home/files/images")
    mipsarc_logo = models.ImageField(upload_to="home/files/images")
    contact_photo_1 = models.ImageField(upload_to="home/files/images")
    contact_photo_2 = models.ImageField(upload_to="home/files/images")
    home_carousel_photo_1 = models.ImageField(upload_to="home/files/images")
    home_carousel_photo_2 = models.ImageField(upload_to="home/files/images")
    home_carousel_photo_3 = models.ImageField(upload_to="home/files/images")
    home_carousel_photo_4 = models.ImageField(upload_to="home/files/images")
    home_carousel_photo_5 = models.ImageField(upload_to="home/files/images")
    donate_photo_1 = models.ImageField(upload_to="home/files/images")
    donate_photo_2 = models.ImageField(upload_to="home/files/images")
    donate_photo_3 = models.ImageField(upload_to="home/files/images")
    donate_photo_4 = models.ImageField(upload_to="home/files/images")
    donate_photo_5 = models.ImageField(upload_to="home/files/images")
    blank_icon = models.ImageField(upload_to="home/files/images")

    class Meta:
        verbose_name_plural = "information"

    def __str__(self):
        return self.site_name


class TeamGoals(models.Model):
    """A small class for holding the organization's goals"""

    team_goal = models.CharField(max_length=250)

    class Meta:
        verbose_name_plural = "Team Goals"

    def __str__(self) -> str:
        return self.team_goal


class SearchSpecialty(models.Model):
    """Holds information related to each SAR Specialty"""

    specialty = models.CharField(max_length=50)
    brief_synopsis = models.CharField(max_length=200)
    long_description_part1 = models.TextField(max_length=400)
    long_descript_part2 = models.TextField(max_length=400)
    icon = models.ImageField(upload_to="home/files/images")
    transparent_icon = models.ImageField(upload_to="home/files/images")
    specialty_photo = models.ImageField(upload_to="home/files/images")

    class Meta:
        verbose_name_plural = "Search Specialties"

    def __str__(self) -> str:
        return self.specialty
