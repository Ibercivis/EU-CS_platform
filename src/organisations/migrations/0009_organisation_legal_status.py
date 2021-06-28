# Generated by Django 2.2.13 on 2021-04-21 11:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('organisations', '0008_auto_20210420_1154'),
    ]

    operations = [
        migrations.AddField(
            model_name='organisation',
            name='legal_status',
            field=models.IntegerField(choices=[(0, 'Profit'), (1, 'Non-profit')], default=0),
        ),
    ]