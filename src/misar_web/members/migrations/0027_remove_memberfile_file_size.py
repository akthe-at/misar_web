# Generated by Django 4.2.7 on 2023-12-08 11:17

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("members", "0026_alter_memberfile_file_size"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="memberfile",
            name="file_size",
        ),
    ]