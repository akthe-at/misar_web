# Generated by Django 5.0.6 on 2024-07-21 14:35

import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0046_siteinfo_just_a_dog_photo'),
    ]

    operations = [
        migrations.AddField(
            model_name='siteinfo',
            name='home_carousel_photo_1',
            field=models.ImageField(default=django.utils.timezone.now, upload_to='home/files/images'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='siteinfo',
            name='home_carousel_photo_2',
            field=models.ImageField(default=django.utils.timezone.now, upload_to='home/files/images'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='siteinfo',
            name='home_carousel_photo_3',
            field=models.ImageField(default=django.utils.timezone.now, upload_to='home/files/images'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='siteinfo',
            name='home_carousel_photo_4',
            field=models.ImageField(default=django.utils.timezone.now, upload_to='home/files/images'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='siteinfo',
            name='home_carousel_photo_5',
            field=models.ImageField(default=django.utils.timezone.now, upload_to='home/files/images'),
            preserve_default=False,
        ),
    ]
