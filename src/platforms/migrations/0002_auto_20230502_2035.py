# Generated by Django 2.2.28 on 2023-05-02 20:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('platforms', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='platform',
            name='dateCreated',
            field=models.DateTimeField(auto_now_add=True, verbose_name='Created date'),
        ),
    ]
