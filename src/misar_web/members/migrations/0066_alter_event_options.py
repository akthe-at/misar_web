# Generated by Django 5.0.4 on 2024-05-13 13:06

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('members', '0065_event_date_posted_event_last_modified'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='event',
            options={'permissions': [('can_view_event', 'Can view event'), ('can_change_event', 'Can change event'), ('can_delete_event', 'Can delete event'), ('can_share_event', 'Can share event')]},
        ),
    ]
