# Generated by Django 3.2.23 on 2023-11-07 23:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('resources', '0046_auto_20220912_0936'),
    ]

    operations = [
        migrations.AlterField(
            model_name='theme',
            name='theme',
            field=models.CharField(max_length=200),
        ),
    ]
