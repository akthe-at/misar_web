# Generated by Django 4.2.7 on 2023-12-07 22:19

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("members", "0024_memberfile_file_size"),
    ]

    operations = [
        migrations.AlterField(
            model_name="memberfile",
            name="file_size",
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
    ]