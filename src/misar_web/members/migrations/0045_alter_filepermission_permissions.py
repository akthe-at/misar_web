# Generated by Django 4.2.7 on 2023-12-17 12:34

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("members", "0044_rename_permission_filepermission_permissions_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="filepermission",
            name="permissions",
            field=models.CharField(
                choices=[
                    ("view", "View"),
                    ("share", "Share"),
                    ("edit", "Edit"),
                    ("delete", "Delete"),
                ],
                default="view",
                max_length=20,
            ),
        ),
    ]
