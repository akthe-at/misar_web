from django.db import models


class SiteInfo(models.Model):
    site_name = models.CharField(max_length=125)
    tagline = models.CharField(max_length=200)
    description = models.TextField()
    mission_statement = models.TextField()
    dispatch_number = models.CharField(default="(800)-818-5645", max_length=20)
    logo = models.ImageField(upload_to="home/files/images")

    def __str__(self):
        return self.site_name

