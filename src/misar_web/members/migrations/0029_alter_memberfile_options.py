# Generated by Django 4.2.7 on 2023-12-10 03:20

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("members", "0028_permission_memberfile_permissions"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="memberfile",
            options={
                "permissions": [
                    ("view", "Can view file"),
                    ("edit", "Can edit file"),
                    ("delete", "Can delete file"),
                    ("share", "Can share file"),
                    ("revoke_share", "Can revoke file sharing"),
                ]
            },
        ),
    ]
