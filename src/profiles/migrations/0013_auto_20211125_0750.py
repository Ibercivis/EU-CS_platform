# Generated by Django 2.2.13 on 2021-11-25 07:50

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('profiles', '0012_profile_manageprojectesfromcountry'),
    ]

    operations = [
        migrations.RenameField(
            model_name='profile',
            old_name='manageProjectesFromCountry',
            new_name='manageProjectsFromCountry',
        ),
    ]