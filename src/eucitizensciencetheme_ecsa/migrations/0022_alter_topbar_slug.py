# Generated by Django 3.2.4 on 2024-07-03 05:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('eucitizensciencetheme', '0021_auto_20240412_1215'),
    ]

    operations = [
        migrations.AlterField(
            model_name='topbar',
            name='slug',
            field=models.CharField(blank=True, max_length=200, null=True),
        ),
    ]