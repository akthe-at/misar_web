# Generated by Django 4.2.7 on 2023-12-03 10:57

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):
    dependencies = [
        ("home", "0026_siteinfo_mailing_address_siteinfo_team_email"),
    ]

    operations = [
        migrations.AddField(
            model_name="siteinfo",
            name="team_goals",
            field=models.TextField(default=django.utils.timezone.now),
            preserve_default=False,
        ),
    ]
