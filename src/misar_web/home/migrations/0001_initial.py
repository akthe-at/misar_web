# Generated by Django 4.2.7 on 2023-11-15 10:45

from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="SiteInfo",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("site_name", models.CharField(max_length=125)),
                ("tagline", models.CharField(max_length=200)),
                ("description", models.TextField()),
            ],
        ),
    ]
