# Generated by Django 2.2 on 2021-11-18 16:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('projects', '0057_project_editors'),
    ]

    operations = [
        migrations.AlterField(
            model_name='translatedproject',
            name='translatedAim',
            field=models.CharField(max_length=10000),
        ),
        migrations.AlterField(
            model_name='translatedproject',
            name='translatedDescription',
            field=models.CharField(max_length=10000),
        ),
        migrations.AlterField(
            model_name='translatedproject',
            name='translatedEquipment',
            field=models.CharField(max_length=10000),
        ),
        migrations.AlterField(
            model_name='translatedproject',
            name='translatedHowToParticipate',
            field=models.CharField(max_length=10000),
        ),
    ]