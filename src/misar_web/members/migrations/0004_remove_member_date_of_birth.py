# Generated by Django 4.2.7 on 2023-11-25 18:46

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("members", "0003_remove_member_member_since_and_more"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="member",
            name="date_of_birth",
        ),
    ]
