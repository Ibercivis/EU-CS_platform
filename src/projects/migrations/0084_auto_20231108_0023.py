# Generated by Django 3.2.23 on 2023-11-08 00:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('projects', '0083_auto_20231108_0020'),
    ]

    operations = [
        migrations.AddField(
            model_name='hastag',
            name='hasTag_de',
            field=models.TextField(null=True),
        ),
        migrations.AddField(
            model_name='hastag',
            name='hasTag_el',
            field=models.TextField(null=True),
        ),
        migrations.AddField(
            model_name='hastag',
            name='hasTag_en',
            field=models.TextField(null=True),
        ),
        migrations.AddField(
            model_name='hastag',
            name='hasTag_es',
            field=models.TextField(null=True),
        ),
        migrations.AddField(
            model_name='hastag',
            name='hasTag_et',
            field=models.TextField(null=True),
        ),
        migrations.AddField(
            model_name='hastag',
            name='hasTag_fr',
            field=models.TextField(null=True),
        ),
        migrations.AddField(
            model_name='hastag',
            name='hasTag_hu',
            field=models.TextField(null=True),
        ),
        migrations.AddField(
            model_name='hastag',
            name='hasTag_it',
            field=models.TextField(null=True),
        ),
        migrations.AddField(
            model_name='hastag',
            name='hasTag_lt',
            field=models.TextField(null=True),
        ),
        migrations.AddField(
            model_name='hastag',
            name='hasTag_nl',
            field=models.TextField(null=True),
        ),
        migrations.AddField(
            model_name='hastag',
            name='hasTag_pt',
            field=models.TextField(null=True),
        ),
        migrations.AddField(
            model_name='hastag',
            name='hasTag_sv',
            field=models.TextField(null=True),
        ),
    ]
