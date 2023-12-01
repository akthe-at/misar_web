# Generated by Django 4.2.7 on 2023-11-30 22:20

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("members", "0008_alter_member_options_remove_member_is_admin_and_more"),
    ]

    operations = [
        migrations.CreateModel(
            name="MemberFile",
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
                ("file_object", models.FileField(upload_to="members/member_files/")),
            ],
        ),
    ]
