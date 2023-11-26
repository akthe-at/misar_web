# Generated by Django 4.2.7 on 2023-11-26 03:32

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):
    dependencies = [
        ("members", "0004_remove_member_date_of_birth"),
    ]

    operations = [
        migrations.AddField(
            model_name="member",
            name="website_join_date",
            field=models.DateField(
                auto_now_add=True, default=django.utils.timezone.now
            ),
            preserve_default=False,
        ),
    ]
