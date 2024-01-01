# Generated by Django 4.2.7 on 2023-12-30 21:38

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("home", "0035_siteinfo_contact_photo_2"),
    ]

    operations = [
        migrations.AddField(
            model_name="siteinfo",
            name="about_photo_3",
            field=models.ImageField(
                default=datetime.datetime(
                    2023, 12, 30, 21, 38, 17, 11243, tzinfo=datetime.timezone.utc
                ),
                upload_to="home/files/images",
            ),
            preserve_default=False,
        ),
    ]
