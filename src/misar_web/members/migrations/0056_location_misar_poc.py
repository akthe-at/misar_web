# Generated by Django 5.0.1 on 2024-01-13 12:35

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("members", "0055_alter_location_website"),
    ]

    operations = [
        migrations.AddField(
            model_name="location",
            name="misar_poc",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="misar_poc",
                to=settings.AUTH_USER_MODEL,
            ),
        ),
    ]
