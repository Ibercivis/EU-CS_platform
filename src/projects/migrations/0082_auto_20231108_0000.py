# Generated by Django 3.2.23 on 2023-11-08 00:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('projects', '0081_searchstats_count'),
    ]

    operations = [
        migrations.AddField(
            model_name='topic',
            name='topic_de',
            field=models.TextField(null=True),
        ),
        migrations.AddField(
            model_name='topic',
            name='topic_el',
            field=models.TextField(null=True),
        ),
        migrations.AddField(
            model_name='topic',
            name='topic_en',
            field=models.TextField(null=True),
        ),
        migrations.AddField(
            model_name='topic',
            name='topic_es',
            field=models.TextField(null=True),
        ),
        migrations.AddField(
            model_name='topic',
            name='topic_et',
            field=models.TextField(null=True),
        ),
        migrations.AddField(
            model_name='topic',
            name='topic_fr',
            field=models.TextField(null=True),
        ),
        migrations.AddField(
            model_name='topic',
            name='topic_hu',
            field=models.TextField(null=True),
        ),
        migrations.AddField(
            model_name='topic',
            name='topic_it',
            field=models.TextField(null=True),
        ),
        migrations.AddField(
            model_name='topic',
            name='topic_lt',
            field=models.TextField(null=True),
        ),
        migrations.AddField(
            model_name='topic',
            name='topic_nl',
            field=models.TextField(null=True),
        ),
        migrations.AddField(
            model_name='topic',
            name='topic_pt',
            field=models.TextField(null=True),
        ),
        migrations.AddField(
            model_name='topic',
            name='topic_sv',
            field=models.TextField(null=True),
        ),
    ]
