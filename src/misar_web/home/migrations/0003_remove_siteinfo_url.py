# Generated by Django 4.2.7 on 2023-11-15 11:32

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("home", "0002_siteinfo_url"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="siteinfo",
            name="url",
        ),
    ]
