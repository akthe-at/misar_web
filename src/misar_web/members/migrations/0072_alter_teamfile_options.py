# Generated by Django 5.0.6 on 2024-05-31 16:50

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('members', '0071_alter_teamfile_options_and_more'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='teamfile',
            options={'verbose_name': 'Team File', 'verbose_name_plural': 'Team Files'},
        ),
    ]