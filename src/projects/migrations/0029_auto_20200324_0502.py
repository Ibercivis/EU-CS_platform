# Generated by Django 2.2.10 on 2020-03-24 05:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('projects', '0028_auto_20200324_0454'),
    ]

    operations = [
        migrations.AlterField(
            model_name='project',
            name='description',
            field=models.CharField(max_length=3000),
        ),
    ]