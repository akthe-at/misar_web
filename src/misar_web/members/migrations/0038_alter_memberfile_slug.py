# Generated by Django 4.2.7 on 2023-12-15 04:04

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("members", "0037_memberfile_owner"),
    ]

    operations = [
        migrations.AlterField(
            model_name="memberfile",
            name="slug",
            field=models.SlugField(editable=False, max_length=255, unique=True),
        ),
    ]