# Generated by Django 4.2.7 on 2023-11-25 13:30

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("home", "0021_alter_siteinfo_logo"),
    ]

    operations = [
        migrations.AlterField(
            model_name="siteinfo",
            name="logo",
            field=models.ImageField(upload_to="misar_web/static/images/"),
        ),
    ]
