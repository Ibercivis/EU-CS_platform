# Generated by Django 2.2.28 on 2023-04-08 13:47

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('projects', '0073_auto_20230408_1346'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='searchstats',
            name='count',
        ),
    ]