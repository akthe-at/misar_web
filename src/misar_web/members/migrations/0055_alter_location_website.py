# Generated by Django 4.2.7 on 2024-01-07 04:33

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("members", "0054_alter_event_date_alter_event_end_time_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="location",
            name="website",
            field=models.URLField(
                blank=True, max_length=75, null=True, verbose_name="Location Website"
            ),
        ),
    ]
