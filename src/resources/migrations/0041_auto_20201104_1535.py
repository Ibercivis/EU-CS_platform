# Generated by Django 2.2.13 on 2020-11-04 14:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('resources', '0040_unapprovedresources'),
    ]

    operations = [
        migrations.AlterField(
            model_name='resource',
            name='featured',
            field=models.BooleanField(default=False),
        ),
    ]