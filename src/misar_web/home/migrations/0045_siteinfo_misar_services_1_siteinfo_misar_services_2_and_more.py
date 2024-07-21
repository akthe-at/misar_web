# Generated by Django 5.0.6 on 2024-07-21 12:02


import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("home", "0044_siteinfo_donate_photo_4_siteinfo_donate_photo_5"),
    ]
    operations = [
        migrations.AddField(
            model_name="siteinfo",
            name="misar_services_1",
            field=models.ImageField(
                default=django.utils.timezone.now, upload_to="home/files/images"
            ),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="siteinfo",
            name="misar_services_2",
            field=models.ImageField(
                default=django.utils.timezone.now, upload_to="home/files/images"
            ),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="siteinfo",
            name="misar_services_3",
            field=models.ImageField(
                default=django.utils.timezone.now, upload_to="home/files/images"
            ),
            preserve_default=False,
        ),
    ]
